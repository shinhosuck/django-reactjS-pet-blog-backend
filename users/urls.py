from django.urls import path
from . views import (
    user_register_view,
    retrieve_token_view,
    user_update_profile_view,
    user_detail_view,
    get_users_view,
)

app_name = 'users'


urlpatterns = [
    path('register/', user_register_view, name='register'),
    path('login/', retrieve_token_view, name='login'),
    path('update/<int:id>/profile/', user_update_profile_view, name='update-profile'),
    path('<int:id>/detail/', user_detail_view, name='user-detail'),
    path('users/', get_users_view, name='users')
]