from .models import Topic, Post
from django.contrib.auth.models import User
from .utils import fetch_host
from django.forms.models import model_to_dict
from collections import OrderedDict



# This view is intended for changing
# image url domain from local:8000 to pythonanywhere.com
def set_images_url_view(request):
    if request.get_host() != '127.0.0.1:8000':
        topics = Topic.objects.all()
        posts = Post.objects.all()
        users = User.objects.all()

        for topic in topics:
            topic.image_url = f'{fetch_host(request)}{topic.image.url}'
            topic.save()

        for post in posts:
            post.image_url = f'{fetch_host(request)}{post.image.url}'
            post.save()

        for user in users:
            user.profile.image_url = f'{fetch_host(request)}{user.profile.image.url}'
            user.profile.save()
    else:
        pass
       
    return {}