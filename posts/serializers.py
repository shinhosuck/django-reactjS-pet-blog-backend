from rest_framework import serializers
from rest_framework.reverse import reverse
from . models import Post, Topic, Comment



class TopicSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(many=False)
    topic_url = serializers.SerializerMethodField(method_name='get_topic_url', read_only=True)
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
            'topic_url',
            'image_url',
            'topic_post_set_likes'
        ]

    def get_topic_url(self, obj):
        request = self.context['request']
        url = reverse('posts:topic-detail', kwargs={'id':obj.id}, request=request)
        return url
    
    def get_image_url(self, obj):
        protocal = ''
        host = self.context['request'].get_host()
        if host == '127.0.0.1:8000' or host == 'localhost:8000':
            protocal = 'http://'
        else:
            protocal = 'https://' 
        url = f'{protocal}{host}{obj.image.url}'
        return url
    
    def get_post_count(self, obj):
        post_count = obj.post_set.count()
        return post_count
    
    def get_topic_post_set_likes(self, obj):
        like_count = [obj.like.count() for obj in obj.post_set.all().prefetch_related('like')]
        return sum(like_count)
    
    
class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(many=False, required=False)
    topic = serializers.StringRelatedField(many=False, required=False)
    image = serializers.ImageField(required=False)
    like = serializers.StringRelatedField(many=True, required=False)
    comments = serializers.StringRelatedField(many=True, required=False)

    class Meta:
        model = Post 
        fields = [
            'id',
            'topic',
            'title',
            'author',
            'image',
            'image_url',
            'content',
            'date_posted',
            'date_updated',
            'like',
            'num_of_replies',
            'comments',
            'featured'
        ]


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(many=False, required=False)
    post = serializers.StringRelatedField(many=False, required=False)

    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'post',
            'content',
            'date_posted',
            'date_updated'
        ]