from rest_framework import serializers
from . models import Post, Topic, PostReply



class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic 
        exclude = ['image']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post 
        fields = '__all__'


class PostReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReply 
        fields = '__all__'