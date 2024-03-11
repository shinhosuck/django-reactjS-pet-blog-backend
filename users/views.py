from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from collections import OrderedDict

# serializer
from . serializers import (
    UserRegisterSerializer,
    UpdateProfileSerializer
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
    IsAuthenticated
)
from posts.views import fetch_host


@api_view(['POST'])
def user_register_view(request):
    username = request.data['username']
    if User.objects.filter(username__iexact=username).first():
        message = {
            "error":f'Username \'{username}\' already exists.',
            'status':status.HTTP_400_BAD_REQUEST
        }
        return Response(message)

    serializer = UserRegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        profile = user.profile
        profile.image_url = f'{fetch_host(request)}{profile.image.url}'
        profile.save()

        message = {
            **serializer.data,
            'message':'Successfully registered!',
            'status':status.HTTP_201_CREATED
        }
        return Response(message)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def retrieve_token_view(request):
    data = request.data 
    username = data['username']
    password = data['password']
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        message = {
            'error':'User does not exist.',
            'status':status.HTTP_400_BAD_REQUEST
        }
        return Response(message)
    
    if user.check_password(password):
        token = Token.objects.get(user=user).key
        message = {
            'token':token, 
            'username':user.username, 
            'profile_image_url': user.profile.image_url,
            'num_of_posts': user.post_set.all().count() or 0,
            'num_of_comments':user.comment_set.all().count() or 0,
            'message':'Successfully authenticated'
        }
        return Response(message, status=status.HTTP_202_ACCEPTED)
    return Response({'error':'password or username did not match'}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def user_update_profile_view(request, id):

    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        message = {'error': 'User does not exist.'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    
    data = OrderedDict()
    data.update(request.data)
    data['user'] = user.id
    serializer = UpdateProfileSerializer(user, data=data)
    
    if serializer.is_valid():
        serializer.save()
        message = {'message': 'Profile updated successfully.'}
        return Response(message, status=status.HTTP_202_ACCEPTED)
    return Response({**serializer.errors, 'message': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_users_view(request):
    users = User.objects.all()
    for user in users:
        user.profile.image_url = f'{fetch_host(request)}{user.profile.image.url}'
        user.profile.save()
    serializer = UserRegisterSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def user_detail_view(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist :
        message = {'error': 'User does not exist.'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    serializer = UserRegisterSerializer(user)
    return Response(serializer.data)


