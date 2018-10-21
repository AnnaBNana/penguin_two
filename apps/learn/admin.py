from django.contrib import admin
from .models import Category, Article
from django_summernote.admin import SummernoteModelAdmin

from adminsortable.admin import SortableAdmin

class ArticleAdmin(SummernoteModelAdmin, SortableAdmin):
    search_fields = [
        "headline",
        "text",
        "category__name"
    ]
    list_filter = [
        "category__name"
    ]

class CategoryAdmin(SortableAdmin):
    search_fields = [
        "name"
    ]


admin.site.register(Category,CategoryAdmin)
admin.site.register(Article,ArticleAdmin)
