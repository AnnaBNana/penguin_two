from django.shortcuts import render
from .models import Post

def index(request, id=-1):
    if id < 0:
        try:
            post = Post.objects.latest('updated_at')
        except Post.DoesNotExist:
            post = None
    else:
        post = Post.objects.get(id=id)
    if post:
        post_length = len(post.text)
        slice_length = post_length if post_length < 550 else 550
    else:
        slice_length = 0
    context = {
        'post': post,
        'slice_length':  slice_length,
        'recent_blogs': blog_list(),
    }
    return render(request, 'blog/index.html', context)


def blog(request,id):
    post = Post.objects.get(id=id)
    context = {
        'post': post,
    }
    return render(request, 'blog/index.html', context)

################ HELPER FUNCTIONS ################

def blog_list():
    blogs = Post.objects.all().order_by("-updated_at")
    return blogs
