from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<str:username>", views.profile, name="profile"),
    path("following", views.following, name="following"),
    path("saved", views.saved, name="saved"),
    path("createpost", views.create_post, name="createpost"),
    path("post/<int:id>/like", views.like_post, name="likepost"),
    path("post/<int:id>/unlike", views.unlike_post, name="unlikepost"),
    path("post/<int:id>/save", views.save_post, name="savepost"),
    path("post/<int:id>/unsave", views.unsave_post, name="unsavepost"),
    path("post/<int:post_id>/comments", views.comment, name="comments"),
    path("post/<int:post_id>/write_comment", views.comment, name="writecomment"),
    path("post/<int:post_id>/delete", views.delete_post, name="deletepost"),
    path("<str:username>/follow", views.follow, name="followuser"),
    path('profile/edit/<str:username>/', views.edit_profile, name='editprofile'), 
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
