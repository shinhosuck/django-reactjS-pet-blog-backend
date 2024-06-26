from rest_framework import serializers
from rest_framework.reverse import reverse
from django.db.models import Count
from django.contrib.auth import get_user_model
from . models import (
    Post, 
    Topic, 
    Comment, 
    Message,
    NewsLetterSubscription,
)
from utils.get_host import fetch_host
User = get_user_model()


class TopicSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(many=False)
    image_url = serializers.SerializerMethodField(method_name='get_image_url', read_only=True)
    post_count = serializers.SerializerMethodField(method_name='get_post_count', read_only=True)
    topic_post_set_likes = serializers.SerializerMethodField(method_name="get_topic_post_set_likes", read_only=True)

    class Meta:
        model = Topic 
        fields = [
            'id',
            'author',
            'name',
            'description',
            'post_count',
            'created',
            'image_url',
            'topic_post_set_likes'
        ]
 
    def get_image_url(self, obj):
        host = fetch_host(self.context['request'])
        url = f'{host}{obj.image.url}'
        return url
    
    def get_post_count(self, obj):
        post_count = obj.post_set.count()
        return post_count
    
    def get_topic_post_set_likes(self, obj):
        like_count = [obj.likes.count() for obj in obj.post_set.prefetch_related('likes')]
        return sum(like_count)
    
    
class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(many=False, required=False)
    topic = serializers.StringRelatedField(many=False, required=False)
    author_profile_image_url = serializers.SerializerMethodField(method_name='get_author_profile_image_url', read_only=True)
    image_url = serializers.SerializerMethodField(method_name='get_image_url', read_only=True)
    qs_count = serializers.SerializerMethodField(method_name='get_qs_count', read_only=True)
    likes = serializers.SerializerMethodField(read_only=True, method_name='get_likes')
    image = serializers.ImageField(use_url=False, required=False)

    
    class Meta:
        model = Post 
        fields = [
            'id',
            'image',
            'topic',
            'title',
            'author',
            'author_profile_image_url',
            'image_url',
            'content',
            'date_posted',
            'featured',
            'qs_count',
            'likes'
        ]


    def get_image_url(self, obj):
        host = fetch_host(self.context['request'])
        url = f"{host}{obj.image.url}"
        return url
    
    def get_qs_count(self, obj):
        comment = obj.comments.aggregate(comment_count=Count('post'))
        likes = obj.likes.count()
        return {**comment, 'like_count':likes}
    
    def get_author_profile_image_url(self, obj):
        host = fetch_host(self.context['request'])
        img_url = f"{host}{obj.author.profile.image.url}"
        return img_url
    
    def get_likes(self, obj):
        users = obj.likes.all().values_list('username', flat=True)
        return users


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(many=False, required=False)
    post = serializers.StringRelatedField(many=False, required=False)
    post_id = serializers.PrimaryKeyRelatedField(source='post', read_only=True)
    post_likes = serializers.SerializerMethodField(method_name='get_post_likes', read_only=True)
    user_profile_image_url = serializers.SerializerMethodField(method_name='get_user_profile_image_url', read_only=True)
    parent_id = serializers.PrimaryKeyRelatedField(source='parent', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'user_profile_image_url',
            'post',
            'post_id',
            'content',
            'date_posted',
            'date_updated',
            'post_likes',
            'parent_id'
        ]

    def get_post_likes(self, obj):
        if obj.post:
            post_likes = obj.post.likes.values_list('username', flat=True)
            return post_likes
        return None
    
    def get_user_profile_image_url(self, obj):
        host = fetch_host(self.context['request'])
        url = f"{host}{obj.user.profile.image.url}"
        return url


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['email', 'content']


class NewsLetterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsLetterSubscription
        fields = ['first', 'last', 'email']
        