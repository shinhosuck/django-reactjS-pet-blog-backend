from . models import Post, Topic, Comment
from users.models import Profile
from django.contrib.auth.models import User
from collections import OrderedDict
from django.forms.models import model_to_dict
import datetime
from django.utils import timezone
# serializer
from . serializers import (
    PostSerializer,
    TopicSerializer,
    CommentSerializer
)

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
    renderer_classes,
    parser_classes,
    authentication_classes,
    permission_classes,
    api_view
)



def fetch_host(request):
    if request.get_host() == '127.0.0.1:8000':
        return f'http://{request.get_host()}'
    return f'https://{request.get_host()}'
    

@api_view(['GET'])
@permission_classes([AllowAny])
def topics_view(request):
    topics = Topic.objects.all()
    for topic in topics:
        topic.total_post = topic.post_set.all().count()
        topic.image_url = f'{fetch_host(request)}{topic.image.url}'
        topic.save()
    serializer = TopicSerializer(topics, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def post_list_view(request):
    formated_data = []
    posts = Post.objects.all()

    for post in posts:
        post.image_url = f'{fetch_host(request)}{post.image.url}'
        post.save()
        print(post.image_url)
    serializer = PostSerializer(posts, many=True)
    for obj in serializer.data:
        obj['author'] = User.objects.get(id=obj['author']).username
        obj['topic'] = Topic.objects.get(id=obj['topic']).name
        formated_data.append(obj)
    return Response(formated_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def post_detail_view(request, id):
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        error = {'message':'Post does not exist.'}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)
    serializer = PostSerializer(post)
    usernames = []
    for value in serializer['like'].value:
        usernames.append(User.objects.get(id=value).username)
    username = User.objects.get(id=serializer.data['author']).username
    topic = Topic.objects.get(id=serializer.data['topic']).name
    data = {**serializer.data, 'author':username, 'topic':topic, 'like':usernames}
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@parser_classes([MultiPartParser, FormParser])
def create_post_view(request, format=None):
    data = OrderedDict()
    data.update(request.data)
    data['author'] = request.user.id
    topic = Topic.objects.filter(name__iexact=data['topic']).first()
    data['topic'] = topic.id
    serializer = PostSerializer(data=data)

    if serializer.is_valid():
        obj = serializer.save()
        url = f'{fetch_host(request)}{obj.image.url}'
        obj.create_image_url(url)
        obj.update_total_post()
        obj.save()
        message = {**serializer.data, 'message':'Successfully created'}
        return Response(message, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@parser_classes([MultiPartParser, FormParser])
def update_post_view(request, id, format=None):
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        message = {'error': 'Post does not exist.'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    
    data = OrderedDict()
    data.update(request.data)
    data['author'] = request.user.id
    data['topic'] = Topic.objects.filter(name__iexact=data['topic']).first().id
    serializer = PostSerializer(post, data=data)

    if serializer.is_valid():
        obj = serializer.save()
        url =  f'{fetch_host(request)}{obj.image.url}'
        obj.create_image_url(url)
        obj.update_total_post()
        obj.save()
        message = {**serializer.data, 'message':'Successfully updated'}
        return Response(message, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def my_post_view(request):
   formated_data = []
   user = request.user
   posts = user.post_set.all()
   if posts.count():
        serializer = PostSerializer(posts, many=True)
        for obj in serializer.data:
            obj['author'] = User.objects.get(id=obj['author']).username
            obj['topic'] = Topic.objects.get(id=obj['topic']).name
            formated_data.append(obj)
        return Response(formated_data, status=status.HTTP_200_OK)
   message = {'error':'You do not have any posts.'}
   return Response(message, status=status.HTTP_400_BAD_REQUEST)
   

@api_view(['GET']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def my_comments_view(request):
   user = request.user
   comments = user.comment_set.all()
   serializer = CommentSerializer(comments, many=True)
   for obj in serializer.data:
       post = Post.objects.get(id=obj['post'])
       obj['replied_to'] = post.title
       obj['post_author'] = post.author.username
   return Response(serializer.data)


@api_view(['DELETE']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delete_comment_view(request, id):
    user = request.user
    comment = Comment.objects.filter(id=id, user=user).first()
    if comment:
        post = comment.post
        post.num_of_replies - 1
        post.save()
        comment.delete()
    user_comments = user.comment_set.all()
    if user_comments.exists():
        serializer = CommentSerializer(user_comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    message = {'message': 'You do not have any comments.'}
    return Response(message, status=status.HTTP_200_OK)


@api_view(['PUT']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_comment_view(request, id):
    try:
        comment = Comment.objects.get(id=id)
    except Comment.DoesNotExist:
        message = {'error': 'Comment does not exist.'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    data = OrderedDict()
    data.update(request.data)
    data['user'] = request.user.id
    data['post'] = comment.post.id
    serializer = CommentSerializer(comment, data=data)
    if serializer.is_valid():
        serializer.save()
        objs = CommentSerializer(request.user.comment_set.all(), many=True)
        return Response(objs.data, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delete_post_view(request, id):
    user = request.user
    try:
        post = Post.objects.get(author=user, id=id)
    except Post.DoesNotExist:
        message = {
            'error':f"You do not have the credential to delete post or the post does not exist"
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    topic = Topic.objects.get(id=post.topic.id)
    topic.total_post = topic.total_post - 1
    topic.save()
    post.delete()
    message = {'message': f'Post "{post.title}" has been deleted successfully.'}
    return Response(message, status=status.HTTP_200_OK)


@api_view(['POST']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_post_like_view(request, id):
    user = request.user
    if user.is_authenticated:
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            message = {
                'error':'Post does not exist'
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        
        if user not in post.like.all():
            post.like.add(user)
            post.save()
            message = {'message': 'Thank you for liking.'}
            return Response(message, status=status.HTTP_200_OK)
        return Response({'error': 'Sorry, you can only like once.'})
    message = {'error': 'You are not authenticated.'}
    return Response(message, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def create_reply_post_view(request, id):
    data = OrderedDict()
    data.update(request.data)
    data['user'] = request.user.id
    data['post'] = Post.objects.get(id=id).id
    serializer = CommentSerializer(data=data)
    if serializer.is_valid():
        reply = serializer.save()
        reply.update_total_post_replies()
        message = {**serializer.data, 'message':'Successfully created.'}
        return Response(message, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def already_has_reply_post_view(request, id):
    post = Post.objects.get(id=id)
    try:
        replied_post = Comment.objects.filter(post=post).get(user=request.user)
    except Comment.DoesNotExist:
        return Response({'message':'Can reply'})
    serializer = CommentSerializer(replied_post)
    return Response(serializer.data)


@api_view(['GET'])
def get_post_comments_view(request, id):
    formated_data = []
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return Response({'error': 'Post does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    post_comments = post.comment_set.all()
    if post_comments.count():
        serializer = CommentSerializer(post_comments, many=True)
        for obj in serializer.data:
            obj['user'] = User.objects.get(id=obj['user']).username
            obj['user_image_url'] = User.objects.get(username=obj['user']).profile.image_url
            obj['post'] = Post.objects.get(id=obj['post']).title
            formated_data.append(obj)
        return Response(formated_data, status=status.HTTP_200_OK)
    return Response({'error': 'Replied posts not available'})


