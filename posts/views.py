from . models import Post, Topic, Comment
from django.contrib.auth.models import User
from collections import defaultdict, OrderedDict
from django.forms.models import model_to_dict
from django.db.models import (
    Count, Q, F, Sum, Min, Avg, Max
)
from django.contrib.auth.models import User
from django.shortcuts import HttpResponse

from utils.get_host import fetch_host
from utils.send_email import send_email

# serializer
from . serializers import (
    PostSerializer,
    TopicSerializer,
    CommentSerializer,
    MessageSerializer,
    NewsLetterSubscriptionSerializer
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


@api_view(['GET'])
@permission_classes([AllowAny])
def topics_view(request):
    topics = Topic.objects.all().prefetch_related('author', 'post_set')
    serializer = TopicSerializer(topics, many=True, context={'request':request})
    return Response(serializer.data, status=status.HTTP_200_OK)
    

@api_view(['GET'])
@permission_classes([AllowAny])
def topic_detail_view(request, id):
    try:
        topic = Topic.objects.get(id=id)
    except Topic.DoesNotExist:
        message = {'error': 'Topic not found'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    serializer = TopicSerializer(topic, context={'request':request})
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
    posts = Post.objects.prefetch_related('likes', 'topic', 'author', 'comments')
    serializer = PostSerializer(posts, context={'request': request}, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def post_detail_view(request, id):
    try:
        post = Post.objects.select_related('topic', 'author')\
        .prefetch_related('likes').get(id=id)
    except Post.DoesNotExist:
        message = {'error':'Post not found.'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    serializer = PostSerializer(post, context={'request':request})
    return Response(serializer.data, status=status.HTTP_200_OK)


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
    
    serializer = PostSerializer(data=request.data, context={'request':request})
    if serializer.is_valid(raise_exception=True):
        new_post = serializer.save(author=request.user, topic=topic)
        new_post.save()
        message = {**serializer.data, 'message':'Successfully created'}
        return Response(message, status=status.HTTP_201_CREATED)
    

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
        serializer = PostSerializer(post, data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            message = {**serializer.data, 'message':'Successfully updated'}
            return Response(message, status=status.HTTP_202_ACCEPTED)
        message = {'error': serializer.errors}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delete_post_view(request, id):
    user = request.user
    post = Post.objects.filter(id=id, author=user).first()

    if post == None:
        message = {'error':"Post not found"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    
    post.delete()
    message = {'message': f'Post has been deleted successfully.'}
    return Response(message, status=status.HTTP_200_OK)


@api_view(['POST']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_post_like_view(request, id):
    user = request.user
    try:
        post = Post.objects.prefetch_related('likes').get(id=id)
    except Post.DoesNotExist:
        message = {'error':'Post not found'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    
    post.likes.add(user)
    post.save()
    message = {'message': 'Submmision was successfull.'}
    return Response(message, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def get_post_comments_view(request, id):
    try:
        post = Post.objects.prefetch_related('likes', 'comments').get(id=id)
    except Post.DoesNotExist:
        message = {'error':'Post does not exist.'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    
    comments = post.comments.filter(parent=None).select_related('user')
    
    if comments.exists():
        serializer = CommentSerializer(comments, many=True, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    message = {'error':'No comments available'}
    return Response(message)


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
    
    serializer = CommentSerializer(data=request.data, context={'request':request})

    if serializer.is_valid(raise_exception=True):
        serializer.save(user=user, post=post)
        message = {**serializer.data,'message':'successfully created.'}
        return Response(message, status=status.HTTP_201_CREATED)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def create_child_comment(request, id):
    user = request.user
    post_id = request.data.get('postId')
    try:
        comment = Comment.objects.get(id=id)
    except Comment.DoesNotExist:
        message = {'error': 'Comment does not exist.'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CommentSerializer(data=request.data, context={'request':request})

    if serializer.is_valid(raise_exception=True):
        post = Post.objects.filter(id=post_id).first()
        comment = serializer.save(user=user, post=post, parent=comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    message = {'error':serializer.errors}
    return Response(message, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_comment_view(request, id):
    user = request.user
    try:
        comment = Comment.objects.get(id=id, user=user)
    except Comment.DoesNotExist:
        message = {'error': 'comment not found.'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CommentSerializer(comment, data=request.data, context={'request':request})

    if serializer.is_valid():
        serializer.save()
        message = {'message':'comment successfully updated.'}
        return Response({**serializer.data, **message}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delete_comment_view(request, id):
    try:
        comment = Comment.objects.get(id=id, user=request.user)
    except Comment.DoesNotExist:
        message = {'error':'comment not found.'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    
    comment.delete()      
    message = {
        'message': 'comment has been successfully deleted.',
    }
    return Response(message, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def comment_children_comment_view(request, id):
    try:
        comment = Comment.objects.prefetch_related('children').get(id=id)
    except Comment.DoesNotExist:
        message = {'error':'Comment does not exist.'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    comments = comment.children.all()

    if comments.exists():
        serializer = CommentSerializer(comments, many=True, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    message = {'error':'No comments'}
    return Response(message)


@api_view(['GET']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def my_post_view(request):
   user = request.user
   posts = user.posts.prefetch_related('likes', 'topic', 'author')
   if posts.count():
        serializer = PostSerializer(posts, context={'request':request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
   
   message = {'message':'No post available.'}
   return Response(message, status=status.HTTP_400_BAD_REQUEST)
   

@api_view(['GET']) 
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def my_comments_view(request):
    user = request.user
    comments = user.comment_set.select_related('post').prefetch_related('post__likes')
    serializer = CommentSerializer(comments, many=True, context={'request':request})
    return Response(serializer.data)


@api_view(['GET'])
def search_view(request):
    search_results = []
    search = str(request.data.get('q')).split()

    for word in search:
        post_results = [
            post for post in Post.objects.filter(
            Q(title__icontains=word) | Q(content__icontains=word)).values()
        ]
        if search_results:
            search_results.extend(post_results)
        else:
            search_results = post_results

    if search_results:
        qs = []
        search_results = [dict(post) for post in set(tuple(post.items()) for post in search_results)]
        for post in search_results:
            qs.append(Post.objects.get(id=post.get("id")))
        serializer = PostSerializer(qs, many=True, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    message = {
            'error': 'Your search did not return anything',
            'status': status.HTTP_404_NOT_FOUND
        }
    return Response(message)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_message_view(request):
    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        obj = serializer.save()
        send_email(request, 'Message Received', obj.email)
        message = {'message': 'Message successfully sent.'}
        return Response(message, status=status.HTTP_201_CREATED)
    
    message = {'error': 'Unable to send message.'}
    return Response(message, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def news_letter_subscription_view(request):
    serializer = NewsLetterSubscriptionSerializer(data=request.data)
    if serializer.is_valid():
        obj = serializer.save()
        send_email(request,"Newsletter Subscription", obj.email, f'{obj.first} {obj.last}')
        message = {'message': 'Successfully subscribed to our newsletter.'}
        return Response(message, status=status.HTTP_201_CREATED)
    
    message = {'error': 'Unable to send message.'}
    return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_follow_view(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        message = {
            'error': 'User does not exist', 
            'status':status.HTTP_400_BAD_REQUEST
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    
    user_profile = request.user.profile
    user_profile.following.add(user)
    user_profile.save()

    message = {
        'message': f'Your are following {user.username}.',
        'status': status.HTTP_202_ACCEPTED
    }
    return Response(message, status=status.HTTP_202_ACCEPTED)