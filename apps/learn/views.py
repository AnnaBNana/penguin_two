from django.shortcuts import render
from .models import Category, Article
from django.db import connection
from django.db.models import Prefetch


def index(request):
    try:
        article = Article.objects.latest("created_at")
    except Article.DoesNotExist:
        article = None
    context = {
        "article": article,
        "all_articles": article_list(),
    }
    print context
    return render(request, 'learn/index.html', context)

def article(request,id):
    context = {
        "article": Article.objects.get(id=id),
        "all_articles": article_list(),
    }
    return render(request, 'learn/index.html', context)

################# HELPER FUNCTIONS #################

def article_list(): 
    articles = Article.objects.all().prefetch_related(Prefetch("category")).order_by("category","-updated_at")
    all_articles = []
    for article in articles:
        if article.category not in all_articles:
            all_articles.append(article.category)
        all_articles.append(article)
    return all_articles