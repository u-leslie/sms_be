from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, Like, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.models import User

# List all posts
@login_required
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')  # Order by latest post
    return render(request, 'posts/post_list.html', {'posts': posts})

# Detail view of a post with comments
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()  # Retrieve all comments related to the post
    return render(request, 'posts/post_detail.html', {'post': post, 'comments': comments})

# Create a new post
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

# Add a comment to a post
@login_required
def add_comment(request, post_id):
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
    return render(request, 'posts/add_comment.html', {'form': form, 'post': post})

# Like or unlike a post
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()  # Unlike if already liked
    return redirect('post_detail', post_id=post.id)

# Follow or unfollow a user
@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    if not created:
        follow.delete()  # Unfollow if already following
    return redirect('post_list')
