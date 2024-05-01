from django.contrib import admin
from . models import Topic, Post, Comment, Message, NewsLetterSubscription





class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']

admin.site.register( Topic, TopicAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'featured', 'author', 'date_posted', 'id']
    search_fields = ['topic__name']

admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'date_posted', 'parent']
    search_fields = ['id', 'user__username', 'post__title', 'post__id', 'parent__id']

admin.site.register(Comment, CommentAdmin)


class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'created']
    search_fields = ['email']

admin.site.register(Message, MessageAdmin)


class NewsLetterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'first', 'last', 'email']
    search_fields = ['email']

admin.site.register(NewsLetterSubscription, NewsLetterSubscriptionAdmin)