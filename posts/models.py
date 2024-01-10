from django.contrib.auth.models import User
from django.db import models
from PIL import Image
import uuid


class Topic(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="topic_images", null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    total_post = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Post(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(default="post_images/default.webp", upload_to="post_images")
    image_url = models.URLField(null=True, blank=True)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    like = models.ManyToManyField(User, blank=True, related_name='post_like')
    num_of_replies = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.image:
            self.image = '/post_images/default.jpg'
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.width > 600 and img.height > 600:
            edited_img = (500, 500)
            img.thumbnail(edited_img)
            img.save(self.image.path)

    def create_image_url(self, url):
        self.image_url = url 
        return self.image_url
    
    def update_total_post(self):
        print('hello world')
        topic_count = Post.objects.filter(topic__name=self.topic.name).count()
        self.topic.total_post += topic_count
        self.topic.save()
        return self.topic.total_post

    class Meta:
        ordering = ["-date_posted"]


class PostReply(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.post.title
    
    def update_total_post_replies(self):
        post = self.post
        post.num_of_replies = post.postreply_set.all().count()
        post.save()
    
    class Meta:
        verbose_name_plural = 'Post Replies'
