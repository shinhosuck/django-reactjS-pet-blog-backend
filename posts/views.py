from . models import Post, Topic, Comment
from django.contrib.auth.models import User
from collections import defaultdict, OrderedDict
from django.forms.models import model_to_dict
from django.db.models import (
    Count, Q, F, Sum, Min, Avg, Max
)
from django.contrib.auth.models import User
from django.shortcuts import HttpResponse
from .utils import fetch_host

# serializer
from . serializers import (
    PostSerializer,
    TopicSerializer,
    CommentSerializer
)

from users.serializers import UserRegisterSerializer

# rest_framework
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import (
    JSONParser,
    MultiPartParser,
    FormParser
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from rest_framework.decorators import (
    parser_classes,
    authentication_classes,
    permission_classes,
    api_view
)


# This view is intended for changing
# image url domain from 127.0.0.1:8000:8000 to pythonanywhere.com
def set_images_url_view(request):
    topics = Topic.objects.all()
    posts = Post.objects.all()
    users = User.objects.all()

    for topic in topics:
        topic.image_url = f'{fetch_host(request)}{topic.image.url}'
        topic.save()

    for post in posts:
        post.image_url = f'{fetch_host(request)}{post.image.url}'
        post.save()

    for user in users:
        user.profile.image_url = f'{fetch_host(request)}{user.profile.image.url}'
        user.profile.save()

    data = [
        {'topics': [model_to_dict(topic) for topic in topics]},
        {'posts': [model_to_dict(post) for post in posts]},
        {'users': [dict(OrderedDict(user)) for user in users.values('id', 'username')]}
    ]
       
    return HttpResponse(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def topics_view(request):
    topics = Topic.objects.all().prefetch_related('author')
    serializer = TopicSerializer(topics, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    

@api_view(['GET'])
@permission_classes([AllowAny])
def topic_detail_view(request, id):
    try:
        topic = Topic.objects.get(id=id)
    except Topic.DoesNotExist:
        message = {'error': 'Topic not found'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    serializer = TopicSerializer(topic)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@parser_classes([MultiPartParser, FormParser])
def create_topic_view(request, format=None):
    serializer = TopicSerializer(data=request.data)

    if serializer.is_valid():
        new_topic = serializer.save()
        new_topic.image_url = f'{fetch_host(request)}{new_topic.image.url}'
        new_topic.user_created_topic = True
        new_topic.save()

        message = {**serializer.data, 'message':'Successfully created'}
        return Response(message, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@parser_classes([MultiPartParser, FormParser])
def update_topic_view(request, id, format=None):
    try:
        topic = Topic.objects.get(id=id, author=request.user)
    except Topic.DoesNotExist:
        message = {'error': 'Topic not found.'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)

    serializer = TopicSerializer(topic, data=request.data)

    if serializer.is_valid():
        serializer.save()
        message = {**serializer.data, 'message':'Successfully created'}
        return Response(message, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delete_topic_view(request, id):
    try:
        topic = Topic.objects.get(id=id)
    except Topic.DoesNotExist:
        message = {'error': 'Topic not found.'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    
    topic.delete()

    message = {'message': f'{topic.name} has been deleted successfully.'}
    return Response(message, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def post_list_view(request):
    posts = Post.objects.all().prefetch_related('like', 'topic', 'author')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def post_detail_view(request, id):
    try:
        post = Post.objects.select_related('topic', 'author').prefetch_related('like').get(id=id)
    except Post.DoesNotExist:
        error = {'message':'Post not found.'}
        return Response(error, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PostSerializer(post)
    author_profile_image_url = post.author.profile.image_url
    usernames = [user.username for user in post.like.all()]

    data = {
        **serializer.data, 
        'author_profile_image_url': author_profile_image_url,
        'like':usernames, 
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@parser_classes([MultiPartParser, FormParser])
def create_post_view(request, format=None):
    try:
        topic = Topic.objects.get(name__iexact=request.data.get('topic'))
    except Topic.DoesNotExist:
        message = {'error': 'Topic not found.'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        new_post = serializer.save()
        new_post.author = request.user
        new_post.topic = topic
        new_post.image_url = f'{fetch_host(request)}{new_post.image.url}'
        new_post.save()

        new_post.topic.update_total_post()

        message = {**serializer.data, 'message':'Successfully created'}
        return Response(message, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@parser_classes([MultiPartParser, FormParser])
def update_post_view(request, id, format=None):
    user = request.user
    post = Post.objects.filter(id=id, author=user).first()

    if post == None:
        message = {'error': 'Post not found.'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    
    else:
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            updated_post = serializer.save()
            if serializer.validated_data.get('image'):
                updated_post.image_url = f'{fetch_host(request)}{updated_post.image.url}'
            updated_post.save()

            message = {**serializer.data, 'message':'Successfully updated'}
            return Response(message, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delete_post_view(request, id):
    user = request.user
    post = Post.objects.filter(id=id, author=user).first()

    if post == None:
        message = {'error':"Post not found"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)

    else:
        post.delete()
        post.topic.update_total_post()
        message = {'message': f'Post has been deleted successfully.'}
    return Response(message, status=status.HTTP_200_OK)


@api_view(['POST']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_post_like_view(request, id):
    user = request.user

    try:
        post = Post.objects.prefetch_related('like').get(id=id)
    except Post.DoesNotExist:
        message = {'error':'Post not found'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    
    if user not in post.like.all():
        post.like.add(user)
        post.save()
        message = {'message': 'Submmision was successfull.'}
        return Response(message, status=status.HTTP_200_OK)
    message = {'error': 'You have already submited.'}
    return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_post_comments_view(request, id):
    comment_related_objects = defaultdict()

    try:
        post = Post.objects.select_related('author').prefetch_related('like', 'comments').get(id=id)
    except Post.DoesNotExist:
        message = {'error':'Post not foune.'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    
    comments = post.comments.all().select_related('user', 'user__profile')
    
    if comments.exists():
        for comment in comments:
            comment_related_objects[comment.id.hex] = {
                'user_image_url':comment.user.profile.image_url,
                'user_id': comment.user.id
            }

        serializer = CommentSerializer(comments, many=True)

        for comment_data in serializer.data:
            related_obj = comment_related_objects.get(comment_data['id'].replace('-', ''))
            if related_obj:
                comment_data['user_image_url'] = related_obj['user_image_url']
                comment_data['user_id'] = related_obj['user_id']
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    message = {'error':'comments not available.'}
    return Response(message, status=status.HTTP_404_NOT_FOUND )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def create_comment_view(request, id):
    user = request.user
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        message = {'error': 'Post not found.'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CommentSerializer(data=request.data)

    if serializer.is_valid():
        new_comment = serializer.save()
        new_comment.user = user 
        new_comment.post = post
        new_comment.save()
        comment_count = post.update_total_comment()
        message = {'message':'successfully created.'}
        comment_obj = {**serializer.data,'comment_count':comment_count,}
        return Response({**comment_obj, **message}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_comment_view(request, id):

    try:
        comment = Comment.objects.get(id=id, user=request.user)
    except Comment.DoesNotExist:
        message = {'error': 'comment not found.'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CommentSerializer(comment, data=request.data)

    if serializer.is_valid():
        serializer.save()
        message = {'message':'comment successfully updated.'}
        return Response({**serializer.data, **message}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delete_comment_view(request, id):
    print(request.data)

    try:
        comment = Comment.objects.get(id=id, user=request.user)
    except Comment.DoesNotExist:
        message = {'error':'comment not found.'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    
    post = comment.post
    comment.delete()
    comment_count = post.update_total_comment()

    if request.data.get('isMyComment'):
        comment_count = Comment.objects.filter(user=request.user).count()
        
    message = {
        'message': 'comment has been successfully deleted.',
        'comment_count': comment_count
    }
    return Response(message, status=status.HTTP_200_OK)
    

@api_view(['GET']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def my_post_view(request):
   user = request.user
   posts = user.post_set.all().prefetch_related('like', 'topic', 'author')
   if posts.count():
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
   message = {'message':'No post available.'}
   return Response(message, status=status.HTTP_400_BAD_REQUEST)
   

@api_view(['GET']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def my_comments_view(request):
    user = User.objects.get(username='admin')
    likes_and_post_author = []
    comments = user.comment_set.all().select_related('post').prefetch_related('post__like')

    for comment in comments:
        likes_and_post_author.append({
            comment.id.hex:{
                    'like':[user['username'] for user in UserRegisterSerializer(
                                    comment.post.like.all(), many=True).data], 
                    'post_id':comment.post.id
                }
            })

    serializer = CommentSerializer(comments, many=True)

    for comment in serializer.data:
        for obj in likes_and_post_author:
            if comment['id'].replace('-', '') in obj:
                comment_id = comment['id'].replace('-', '')
                related_obj = obj.get(comment_id)
                comment['post_id'] = related_obj['post_id']
                comment['like'] = related_obj['like']
    return Response(serializer.data)


@api_view(['GET'])
def search_view(request):
    total_results = []
    search = str(request.GET.get('q')).split()

    for word in search:
        post_results = [post for post in Post.objects.filter(
            Q(title__icontains=word) | Q(content__icontains=word)).values()]
        if total_results:
            total_results.extend(post_results)
        else:
            total_results = post_results
    
    total_results = [
        dict(post_set) 
        for post_set in set(tuple(post.items()) 
        for post in total_results)
    ]

    if total_results:
        serializer = PostSerializer(total_results, many=True)
        data = list(serializer.data)
        data.append({'message':'Your search results.'})
        return Response(data, status=status.HTTP_200_OK)
    
    message = {'message': 'No results'}
    return Response(message, status=status.HTTP_404_NOT_FOUND)