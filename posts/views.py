from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, Like, Follow
from .forms import PostForm, CommentForm

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})

@login_required
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'posts/post_list.html', {'posts': posts})

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()
    return render(request, 'posts/post_detail.html', {'post': post, 'form': form})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    Like.objects.get_or_create(user=request.user, post=post)
    return redirect('post_detail', post_id=post.id)

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(CustomUser, id=user_id)
    Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    return redirect('profile', user_id=user_id)
