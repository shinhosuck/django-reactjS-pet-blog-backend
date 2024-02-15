from django.urls import path 
from . views import (
    topics_view,
    post_list_view,
    create_post_view,
    post_detail_view,
    my_post_view,
    update_post_view,
    delete_post_view,
    update_post_like_view,
    create_comment_view,
    already_has_reply_post_view,
    get_post_comments_view,
    my_comments_view,
    delete_comment_view,
    update_comment_view,
)


app_name = 'posts'


urlpatterns = [
    path('topics/', topics_view, name='topics'),
    path('posts/', post_list_view, name='posts'),
    path('create/', create_post_view, name='create'),
    path('post/<uuid:id>/detail/', post_detail_view, name='detail'),
    path('post/<uuid:id>/update/', update_post_view, name='update-post'),
    path('my-post/', my_post_view, name='my-post'),
    path('my-comment/', my_comments_view, name='my-comment'),
    path('comment/<uuid:id>/delete/', delete_comment_view, name='delete-comment'),
    path('comment/<uuid:id>/update/', update_comment_view, name='update-comment'),
    path('post/<uuid:id>/delete/', delete_post_view, name='delete-post'),
    path('update/post/<uuid:id>/like/', update_post_like_view, name='update-like'),
    path('post/<uuid:id>/create/comment/', create_comment_view, name='create-comment'),
    path('post/<uuid:id>/has-reply/', already_has_reply_post_view, name='has-reply'),
    path('post/<uuid:id>/comments/', get_post_comments_view, name='post-comments'),
]