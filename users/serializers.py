
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.db.models import Count
from . models import Profile
from posts.models import Post
from utils.get_host import fetch_host



User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

        extra_kwargs = {
            'password':{
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user
    

class ProfileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(method_name='get_image_url', read_only=True)
    qs_count = serializers.SerializerMethodField(method_name='get_qs_count', read_only=True)
    token = serializers.SerializerMethodField(method_name='get_token', read_only=True)
    class Meta:
        model = Profile
        fields = [
            'token',
            'user', 
            'image_url', 
            'username', 
            'qs_count'
        ]


    def get_image_url(self, obj):
        host = fetch_host(self.context['request'])
        url = f"{host}{obj.image.url}"
        return url
    

    def get_qs_count(self, obj):
        posts = obj.user.posts.prefetch_related('comments')
        comment_count = posts.aggregate(comment_count=Count('comments__post'))
        post_count = posts.aggregate(post_count = Count('author__id'))
        return {**comment_count, **post_count}
    

    def get_token(self, obj):
        user = obj.user
        token = Token.objects.get(user=user).key
        return token

    
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile = Profile.objects.filter(user__id=instance.id).first()
        profile.image = validated_data.get('image')
        profile.username = instance.username
        profile.first_name = instance.first_name
        profile.last_name = instance.last_name
        profile.email = instance.email
        profile.save()
        return instance