from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from collections import OrderedDict
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
    IsAuthenticated
)


@api_view(['POST'])
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
def retrieve_token_view(request):
    data = request.data 
    username = data['username']
    password = data['password']
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        message = {'error':'User does not exist.'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = ProfileSerializer(user.profile, context={'request':request})
    
    if user.check_password(password):
        message = {'message':'Successfully authenticated'}
        message = {**message, **serializer.data}
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
    serializer = ProfileSerializer(user, data=data)
    
    if serializer.is_valid():
        serializer.save()
        message = {'message': 'Profile updated successfully.'}
        return Response(message, status=status.HTTP_202_ACCEPTED)
    return Response({**serializer.errors, 'message': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_users_view(request):
    users = Profile.objects.all()
    serializer = ProfileSerializer(users, many=True, context={'request':request})
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


