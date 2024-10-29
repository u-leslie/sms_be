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
from .forms import ProfileEditForm

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
        followings = Follower.objects.filter(followers=request.user).values_list("user", flat=True        )
        suggestions = (User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
        )
    return render(request,"network/index.html",{"posts": posts,"suggestions": suggestions,"page": "all_posts","profile": False,},)

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render( request, "network/login.html", {"message": "Invalid username and/or password."},)
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
        print(f"---Profile: {profile}---")
        cover = request.FILES.get("cover")
        print(f"---Cover: {cover}---")
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {"message": "Passwords must match."})
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
            return render(request, "network/register.html", {"message": "Username already taken."})
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def profile(request, username):
    user = get_object_or_404(User, username=username)
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
        followings = Follower.objects.filter(followers=request.user).values_list("user", flat=True)
        suggestions = (User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6])
        if request.user in Follower.objects.get(user=user).followers.all():
            follower = True
    follower_count = Follower.objects.get(user=user).followers.all().count()
    following_count = Follower.objects.filter(followers=user).count()
    return render(request,"network/profile.html",{"username": user,"posts": posts,"posts_count": all_posts.count(),"suggestions": suggestions,"page":"profile","is_follower": follower,"follower_count": follower_count,"following_count":following_count,},)

@login_required
def edit_profile(request, username):
    user_profile = get_object_or_404(User, username=username)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=user_profile.username)  # Redirect to the profile page
    else:
        form = ProfileEditForm(instance=user_profile)

    context = {
        'form': form,
        'username': user_profile.username,
    }
    return render(request, 'network/editprofile.html', context)  # Create this template for the edit form


def following(request):
    if request.user.is_authenticated:
        following_user = Follower.objects.filter(followers=request.user).values("user")
        all_posts = Post.objects.filter(creater__in=following_user).order_by("-date_created")
        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get("page")
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)
        followings = Follower.objects.filter(followers=request.user).values_list("user", flat=True)
        suggestions = (User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]) 
        return render(request,"network/index.html",{"posts": posts, "suggestions": suggestions, "page": "following"},)
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
        followings = Follower.objects.filter(followers=request.user).values_list("user", flat=True)
        suggestions = (User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6])
        return render(request,"network/index.html",{"posts": posts, "suggestions": suggestions, "page": "saved"},)
    else:
        return HttpResponseRedirect(reverse("login"))

@login_required
def create_post(request):
    if request.method == "POST":
        text = request.POST.get("text")
        pic = request.FILES.get("picture")
        try:
            Post.objects.create(creater=request.user, content_text=text, content_image=pic)
            return HttpResponseRedirect(reverse("index"))
        except Exception as e:
            return HttpResponse(e)
    else:
        return HttpResponse("Method must be 'POST'")

@login_required
@csrf_exempt
def edit_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user != post.creater:
        return HttpResponse(status=403)
    if request.method == "POST":
        if request.POST.get("edit_mode") == "true":
            post.edit_mode = True
            post.save()
            return redirect("profile", username=request.user.username)
        text = request.POST.get("text")
        pic = request.FILES.get("picture")
        img_chg = request.POST.get("img_change")
        try:
            post.content_text = text
            if img_chg == "true" and pic:
                post.content_image = pic
            post.edit_mode = False
            post.save()
            return redirect("profile", username=request.user.username)  
        except Exception as e:
            print(e)
            return JsonResponse({"success": False, "error": str(e)})
    return HttpResponse(status=405)

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
            print(f"...User: {user}...")
            print(f"...Follower: {request.user}...")
            try:
                (follower, created) = Follower.objects.get_or_create(user=user)
                follower.followers.add(request.user)
                follower.save()
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
                newcomment = Comment.objects.create(post=post, commenter=request.user, comment_content=comment)
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
        if request.method == "POST": 
            try:
                post = Post.objects.get(id=post_id)
                if request.user == post.creater:
                    post.delete() 
                    return redirect("profile", username=request.user.username)
                else:
                    return HttpResponse(status=403)
            except Post.DoesNotExist:
                return HttpResponse(status=404)
        else:
            return HttpResponse("Method must be 'POST'", status=405)
    else:
        return HttpResponse(status=401) 

def followers_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers = Follower.objects.get(user=profile_user).followers.all() 
    return render(request,"network/followers.html",{"profile_user": profile_user,"followers": followers,})

def following_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    following_users = Follower.objects.filter(followers=profile_user).values_list("user", flat=True)
    following = User.objects.filter(id__in=following_users)
    return render(request,"network/following.html",{"profile_user": profile_user,"following": following,},)
