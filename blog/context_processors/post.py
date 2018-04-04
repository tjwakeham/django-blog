from ..models import Post

def posts(request):
    return {
        'all_posts': Post.objects.all()
    }