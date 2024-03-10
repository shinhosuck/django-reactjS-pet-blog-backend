from django.contrib import admin
from . models import Topic, Post, Comment





class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']

admin.site.register( Topic, TopicAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'author', 'date_posted', 'id']
    search_fields = ['topic__name']

admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'date_posted']
    search_fields = ['user__username', 'post__title', 'post__id']

admin.site.register(Comment, CommentAdmin)