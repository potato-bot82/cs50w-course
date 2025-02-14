from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import User, Post, Follow


def index(request):
    # Get all posts, ordered by newest first
    posts = Post.objects.all().order_by("-timestamp")

    # Paginate posts, 10 per page
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "page_obj": page_obj
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def new_post(request):

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Post.objects.create(user=request.user, content=content)
        return redirect("new_post")
    
    posts = Post.objects.all().order_by("-timestamp") # ambil semua postingan, urutkan terbaru

    # Paginate posts, 5 per page
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/new_post.html", {
        "page_obj": page_obj
    })

def profile(request, user_id):
    user = get_object_or_404(User, id=user_id) # get the user or return 404
    posts = Post.objects.filter(user=user).order_by("-timestamp") # get user posts

    # get number of follower and following
    followers_count = Follow.objects.filter(followed=user).count()
    following_count = Follow.objects.filter(follower=user).count()

    # check if the current user is following this profile user
    is_following = Follow.objects.filter(follower=request.user, followed=user).exists()

    return render(request, "network/profile.html", {
        "profile_user": user,
        "posts": posts,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following
    })

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)

    # Check if the user is not trying to follow themselves
    if user_to_follow != request.user:
        # Toggle follow
        follow_relation, created = Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)

        if not created:
            follow_relation.delete()  # Unfollow if already following

    return redirect('profile', user_id=user_id)

@login_required
def following(request):
    # Get all users the current user is following
    following_users = Follow.objects.filter(follower=request.user).values_list('followed', flat=True)

    # Get posts from those users, ordered by most recent
    posts = Post.objects.filter(user__in=following_users).order_by("-timestamp")

    # Paginate posts, 5 per page
    paginator = Paginator(posts, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "page_obj": page_obj
    })

@login_required
def edit_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)

        # Ensure the user is the author of the post
        if post.user != request.user:
            return JsonResponse({"error": "Unauthorized action"}, status=403)

        data = request.POST
        new_content = data.get("content", "").strip()

        if new_content:
            post.content = new_content
            post.save()
            return JsonResponse({"message": "Post updated successfully", "content": post.content})

        return JsonResponse({"error": "Content cannot be empty"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Toggle like status
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        action = "unliked"
    else:
        post.likes.add(request.user)
        action = "liked"

    return JsonResponse({"action": action, "total_likes": post.total_likes()})



