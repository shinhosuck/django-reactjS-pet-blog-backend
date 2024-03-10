from rest_framework import serializers
from . models import Post, Topic, Comment


class TopicSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    author = serializers.StringRelatedField(many=False)
    
    class Meta:
        model = Topic 
        fields = [
            'id',
            'author',
            'name',
            'image',
            'image_url',
            'description',
            'total_post',
            'user_created_topic',
            'created',
            'updated'
        ]


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
            'comments'
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