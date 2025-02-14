
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("new_post/", views.new_post, name="new_post"), # all post page
    path("profile/<int:user_id>/", views.profile, name="profile"), # profile page
    path("follow/<int:user_id>/", views.follow_user, name="follow_user"),
    path("following/", views.following, name="following"), #new following page
    path("edit_post/<int:post_id>/", views.edit_post, name="edit_post"),
    path("toggle_like/<int:post_id>/", views.toggle_like, name="toggle_like")

]
