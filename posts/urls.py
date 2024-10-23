from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),  # Home page showing all posts
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),  # Detail view of a specific post
    path('post/new/', views.create_post, name='create_post'),  # Create new post
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),  # Like or unlike a post
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),  # Add a comment to a post
    path('user/<int:user_id>/follow/', views.follow_user, name='follow_user'),  # Follow or unfollow a user
]
