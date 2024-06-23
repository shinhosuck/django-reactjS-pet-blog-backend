from collections import OrderedDict
from django.http import QueryDict 
from . models import Profile

# serializer
from . serializers import (
    UserRegisterSerializer,
    ProfileSerializer
)

# rest_framework
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import (
    authentication_classes,
    permission_classes,
    parser_classes,
    api_view
)
from rest_framework.parsers import (
    FormParser,
    MultiPartParser
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser
)
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def user_register_view(request):
    username = request.data['username']

    if User.objects.filter(username__iexact=username).first():
        message = {"error":f'Username \'{username}\' already exists.'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserRegisterSerializer(data=request.data, context={'request':request})

    if serializer.is_valid(raise_exception=True):
        serializer.save()
        message = {'message':'Successfully registered!',}
        return Response(message, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def retrieve_token_view(request):
    data = request.data 
    username = data['username']
    password = data['password']
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        message = {'error':'User does not exist.'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    
    if user.check_password(password):
        serializer = ProfileSerializer(user.profile, context={'request':request})
        message = {**serializer.data, 'message':'Successfully authenticated'}
        return Response(message, status=status.HTTP_202_ACCEPTED)
    
    message = {'error':'Password or username did not match'}
    return Response(message, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@parser_classes([MultiPartParser, FormParser])
def update_profile_view(request, format=None):
    user = request.user

    try:
        user = User.objects.get(id=user.id)
    except User.DoesNotExist:
        message = {'error': 'User does not exist.'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    data = OrderedDict()
    data.update(request.data)

    if isinstance(data['image'], str):
        data.pop('image')

    query_dict = QueryDict('', mutable=True)
    query_dict.update(data)

    serializer = ProfileSerializer(user.profile, data=data, context={'request':request})
    
    if serializer.is_valid():
        serializer.save()
        message = {'message': 'Profile updated successfully'}
        return Response({**serializer.data, **message}, status=status.HTTP_202_ACCEPTED)
    
    message = {'error': 'There was an error. Please try again.'}
    return Response(message, status=status.HTTP_400_BAD_REQUEST)


# Admin use only
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_users_view(request):
    user = request.user
    if not user.is_superuser:
        message = {
            'error': 'You are not allowed to perform this action',
            'status': status.HTTP_400_BAD_REQUEST
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    
    users = Profile.objects.all()
    serializer = ProfileSerializer(users, many=True, context={'request':request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def user_detail_view(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist :
        message = {'error': 'User does not exist.'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = ProfileSerializer(user.profile, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def follow_view(request, username):
    choice = request.GET.get('choice')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        message = {
            'error': 'User does not exist', 
            'status':status.HTTP_400_BAD_REQUEST
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    
    current_user = request.user
    profile = user.profile
    message = ''
    
    if choice == 'unfollow':
        profile.follower.remove(current_user.id)
        current_user.profile.follow.remove(profile.user.id)
        message = f'You are now unfollowing {profile.user.username}'
    elif choice == 'follow':
        profile.follower.add(request.user.id)
        current_user.profile.follow.add(profile.user.id)
        message = f'You are now following {profile.user.username}'
    
    serializer = ProfileSerializer(current_user.profile, context={'request': request})
    
    message = {
        'data': serializer.data,
        'message': message,
        'status': status.HTTP_202_ACCEPTED
    }
    return Response(message, status=status.HTTP_202_ACCEPTED)