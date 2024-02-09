from rest_framework import serializers
from . models import Post, Topic, Comment



class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic 
        exclude = ['image']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post 
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'