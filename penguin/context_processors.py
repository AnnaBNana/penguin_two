from apps.learn.models import Article, Category
from apps.blog.models import Post
from django.db.models import Prefetch

def cart_count(request): 
    cart = request.session.get('cart', [])
    return {
       "cart": len(cart)
    }
