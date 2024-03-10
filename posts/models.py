from django.contrib.auth.models import User
from django.db import models
from PIL import Image
import uuid



class Topic(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        editable=False, 
        default=uuid.uuid4
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    image = models.ImageField(
        upload_to="topic_images", 
        default='topic_images/default.webp', 
        null=True, blank=True
    )
    image_url = models.URLField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    total_post = models.IntegerField(default=0, null=True, blank=True)
    user_created_topic = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def update_total_post(self):
        self.total_post = self.post_set.all().count()
        self.save()
        return self.total_post
    
    class Meta:
        ordering = ['name']


class Post(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(
        default="post_images/default.webp", 
        upload_to="post_images", 
        null=True, blank=True
    )
    image_url = models.URLField(null=True, blank=True)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    like = models.ManyToManyField(User, blank=True, related_name='post_like')
    num_of_replies = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.title
 
    def update_total_comment(self):
        comments = self.comments.all()
        self.num_of_replies = comments.count()
        self.save()
        return comments.count()

    class Meta:
        ordering = ["topic"]


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.post.title
    
    class Meta:
        ordering = ["-date_posted"]