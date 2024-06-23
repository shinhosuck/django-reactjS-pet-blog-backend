from django.urls import path
from . views import (
    user_register_view,
    retrieve_token_view,
    update_profile_view,
    user_detail_view,
    get_users_view,
    follow_view
)

app_name = 'users'


urlpatterns = [
    path('register/', user_register_view, name='register'),
    path('login/', retrieve_token_view, name='login'),
    path('update/profile/', update_profile_view, name='update-profile'),
    path('<int:id>/detail/', user_detail_view, name='user-detail'),
    path('users/', get_users_view, name='users'),
    path('follow/user/<str:username>/', follow_view, name='follow'),
]