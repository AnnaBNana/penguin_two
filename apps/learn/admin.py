from django.contrib import admin
from .models import Category, Article
from django_summernote.admin import SummernoteModelAdmin

# Register your models here.
class ArticleAdmin(SummernoteModelAdmin):
    pass

admin.site.register(Category)
admin.site.register(Article,ArticleAdmin)
