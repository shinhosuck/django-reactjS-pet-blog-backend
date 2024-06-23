
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
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
    user = serializers.StringRelatedField(read_only=True)
    image_url = serializers.SerializerMethodField(method_name='get_image_url', read_only=True)
    qs_count = serializers.SerializerMethodField(method_name='get_qs_count', read_only=True)
    token = serializers.SerializerMethodField(method_name='get_token', read_only=True)
    follow = serializers.StringRelatedField(many=True, read_only=True)
    follower = serializers.StringRelatedField(many=True, read_only=True)
    image = serializers.ImageField(use_url=False, required=False)
    
    class Meta:
        model = Profile
        fields = [
            'image',
            'user',
            'user_id',
            'username', 
            'first_name',
            'last_name',
            'email',
            'qs_count',
            'token',
            'image_url', 
            'follow',
            'follower'
        ]

    def get_image_url(self, obj):
        host = fetch_host(self.context['request'])
        url = f"{host}{obj.image.url}"
        return url
    
    def get_qs_count(self, obj):
        posts = obj.user.posts.prefetch_related('comments')
        post_count = posts.aggregate(post_count = Count('author__id'))
        comment_count = obj.user.comment_set.aggregate(comment_count=Count('user__id'))
        return {**comment_count, **post_count}
    
    def get_token(self, obj):
        user = obj.user
        token = Token.objects.get(user=user).key
        return token

    def update(self, instance, validated_data):
        user = instance.user
        user.username = validated_data.get('username', user.username)
        user.first_name = validated_data.get('first_name', user.first_name)
        user.last_name = validated_data.get('last_name', user.last_name)
        user.email = validated_data.get('email', user.email)
        user.save()

        profile = Profile.objects.filter(user=user).first()
        profile.image = validated_data.get('image')
        profile.username = validated_data.get('username')
        profile.first_name = validated_data.get('first_name')
        profile.last_name = validated_data.get('last_name')
        profile.email = validated_data.get('email')
        profile.save()
        return profile