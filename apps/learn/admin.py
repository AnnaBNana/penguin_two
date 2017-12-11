from django.contrib import admin
from .models import Category, Article
from django_summernote.admin import SummernoteModelAdmin

class ArticleAdmin(SummernoteModelAdmin):
    search_fields = [
        "headline",
        "text",
        "category__name"
    ]
    list_filter = [
        "category__name"
    ]

class CategoryAdmin(admin.ModelAdmin):
    search_fields = [
        "name"
    ]


admin.site.register(Category,CategoryAdmin)
admin.site.register(Article,ArticleAdmin)
