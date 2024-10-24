from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json

from .models import *


def index(request):
    all_posts = Post.objects.all().order_by("-date_created")
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get("page")
    if page_number == None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = []
    suggestions = []
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list(
            "user", flat=True
        )
        suggestions = (
            User.objects.exclude(pk__in=followings)
            .exclude(username=request.user.username)
            .order_by("?")[:6]
        )
    return render(
        request,
        "network/index.html",
        {
            "posts": posts,
            "suggestions": suggestions,
            "page": "all_posts",
            "profile": False,
        },
    )


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
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        fname = request.POST["firstname"]
        lname = request.POST["lastname"]
        profile = request.FILES.get("profile")
        print(
            f"--------------------------Profile: {profile}----------------------------"
        )
        cover = request.FILES.get("cover")
        print(f"--------------------------Cover: {cover}----------------------------")

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "network/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            if profile is not None:
                user.profile_pic = profile
            else:
                user.profile_pic = "profile_pic/no_pic.png"
            user.cover = cover
            user.save()
            Follower.objects.create(user=user)
        except IntegrityError:
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, username):
    user = get_object_or_404(User, username=username)
    context1 = {
        "username": user,
    }
    all_posts = Post.objects.filter(creater=user).order_by("-date_created")
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get("page")
    if page_number == None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = []
    suggestions = []
    follower = False
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list(
            "user", flat=True
        )
        suggestions = (
            User.objects.exclude(pk__in=followings)
            .exclude(username=request.user.username)
            .order_by("?")[:6]
        )

        if request.user in Follower.objects.get(user=user).followers.all():
            follower = True

    follower_count = Follower.objects.get(user=user).followers.all().count()
    following_count = Follower.objects.filter(followers=user).count()
    return render(
        request,
        "network/profile.html",
        {
            "username": user,
            "posts": posts,
            "posts_count": all_posts.count(),
            "suggestions": suggestions,
            "page": "profile",
            "is_follower": follower,
            "follower_count": follower_count,
            "following_count": following_count,
        },
    )


def following(request):
    if request.user.is_authenticated:
        following_user = Follower.objects.filter(followers=request.user).values("user")
        all_posts = Post.objects.filter(creater__in=following_user).order_by(
            "-date_created"
        )
        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get("page")
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)
        followings = Follower.objects.filter(followers=request.user).values_list(
            "user", flat=True
        )
        suggestions = (
            User.objects.exclude(pk__in=followings)
            .exclude(username=request.user.username)
            .order_by("?")[:6]
        )
        return render(
            request,
            "network/index.html",
            {"posts": posts, "suggestions": suggestions, "page": "following"},
        )
    else:
        return HttpResponseRedirect(reverse("login"))


def saved(request):
    if request.user.is_authenticated:
        all_posts = Post.objects.filter(savers=request.user).order_by("-date_created")

        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get("page")
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)

        followings = Follower.objects.filter(followers=request.user).values_list(
            "user", flat=True
        )
        suggestions = (
            User.objects.exclude(pk__in=followings)
            .exclude(username=request.user.username)
            .order_by("?")[:6]
        )
        return render(
            request,
            "network/index.html",
            {"posts": posts, "suggestions": suggestions, "page": "saved"},
        )
    else:
        return HttpResponseRedirect(reverse("login"))


@login_required
def create_post(request):
    if request.method == "POST":
        text = request.POST.get("text")
        pic = request.FILES.get("picture")
        try:
            post = Post.objects.create(
                creater=request.user, content_text=text, content_image=pic
            )
            return HttpResponseRedirect(reverse("index"))
        except Exception as e:
            return HttpResponse(e)
    else:
        return HttpResponse("Method must be 'POST'")


@login_required
@csrf_exempt
def edit_post(request, post_id):
    post = Post.objects.get(id=post_id)

    # Check if the user is the creator of the post
    if request.user != post.creater:
        return HttpResponse(status=403)  # Forbidden

    if request.method == "POST":
        # Check if the user is switching to edit mode
        if request.POST.get("edit_mode") == "true":
            post.edit_mode = True
            post.save()
            return redirect("profile", username=request.user.username)

        # Save the edited post
        text = request.POST.get("text")
        pic = request.FILES.get("picture")
        img_chg = request.POST.get("img_change")

        try:
            post.content_text = text  # Update post content
            if img_chg == "true" and pic:
                post.content_image = pic  # Update image if provided

            post.edit_mode = False  # Turn off edit mode after saving
            post.save()

            return redirect(
                "profile", username=request.user.username
            )  # Redirect to profile page
        except Exception as e:
            print(e)
            return JsonResponse({"success": False, "error": str(e)})

    return HttpResponse(status=405)  # Method not allowed


@csrf_exempt
def like_post(request, id):
    if request.user.is_authenticated:
        if request.method == "PUT":
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.likers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse("login"))


@csrf_exempt
def unlike_post(request, id):
    if request.user.is_authenticated:
        if request.method == "PUT":
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.likers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse("login"))


@csrf_exempt
def save_post(request, id):
    if request.user.is_authenticated:
        if request.method == "PUT":
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.savers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse("login"))


@csrf_exempt
def unsave_post(request, id):
    if request.user.is_authenticated:
        if request.method == "PUT":
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.savers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse("login"))


@csrf_exempt
def follow(request, username):
    if request.user.is_authenticated:
        if request.method == "POST":
            user = User.objects.get(username=username)
            print(f".....................User: {user}......................")
            print(
                f".....................Follower: {request.user}......................"
            )
            try:
                # Get or create a follow entry
                (follower, created) = Follower.objects.get_or_create(user=user)
                # Add the logged-in user to followers
                follower.followers.add(request.user)
                follower.save()
                # Redirect back to the homepage to refresh the list
                return HttpResponseRedirect(reverse("index"))
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)
        else:
            return JsonResponse({"error": "Method must be 'POST'"}, status=405)
    else:
        return HttpResponseRedirect(reverse("login"))


@csrf_exempt
def unfollow(request, username):
    if request.user.is_authenticated:
        if request.method == "POST":
            user = User.objects.get(username=username)
            print(f".....................User: {user}......................")
            print(
                f".....................Unfollower: {request.user}......................"
            )
            try:
                # Get the follow entry and remove the user from followers
                follower = Follower.objects.get(user=user)
                follower.followers.remove(request.user)
                follower.save()
                # Redirect back to the homepage to refresh the list
                return HttpResponseRedirect(reverse("index"))
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)
        else:
            return JsonResponse({"error": "Method must be 'POST'"}, status=405)
    else:
        return HttpResponseRedirect(reverse("login"))


@csrf_exempt
def comment(request, post_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            data = json.loads(request.body)
            comment = data.get("comment_text")
            post = Post.objects.get(id=post_id)
            try:
                newcomment = Comment.objects.create(
                    post=post, commenter=request.user, comment_content=comment
                )
                post.comment_count += 1
                post.save()
                print(newcomment.serialize())
                return JsonResponse([newcomment.serialize()], safe=False, status=201)
            except Exception as e:
                return HttpResponse(e)

        post = Post.objects.get(id=post_id)
        comments = Comment.objects.filter(post=post)
        comments = comments.order_by("-comment_time").all()
        return JsonResponse([comment.serialize() for comment in comments], safe=False)
    else:
        return HttpResponseRedirect(reverse("login"))


@csrf_exempt
def delete_post(request, post_id):
    if request.user.is_authenticated:
        if request.method == "POST":  # Accept POST instead of PUT
            try:
                post = Post.objects.get(id=post_id)
                if request.user == post.creater:
                    post.delete()  # Delete the post
                    return redirect(
                        "profile", username=request.user.username
                    )  # Successful deletion
                else:
                    return HttpResponse(status=403)  # Forbidden (not the creator)
            except Post.DoesNotExist:
                return HttpResponse(status=404)  # Post not found
        else:
            return HttpResponse(
                "Method must be 'POST'", status=405
            )  # Method not allowed
    else:
        return HttpResponse(status=401)  # Unauthorized


def followers_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers = Follower.objects.get(
        user=profile_user
    ).followers.all()  # Get all followers
    return render(
        request,
        "network/followers.html",
        {
            "profile_user": profile_user,
            "followers": followers,
        },
    )


# View to show the list of users the profile is following
def following_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    following_users = Follower.objects.filter(followers=profile_user).values_list(
        "user", flat=True
    )
    following = User.objects.filter(
        id__in=following_users
    )  # Get all users being followed
    return render(
        request,
        "network/following.html",
        {
            "profile_user": profile_user,
            "following": following,
        },
    )
