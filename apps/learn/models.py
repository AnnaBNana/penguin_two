from __future__ import unicode_literals
from django.db import models

from adminsortable.models import SortableMixin, SortableForeignKey


# Create your models here.
class Category(SortableMixin):
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order_for_cat']
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=255)
    order_for_cat = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Article(SortableMixin):
    class Meta:
        ordering = ['order_for_art']
    def __unicode__(self):
        return self.headline
    headline = models.CharField(max_length=255)
    text = models.TextField(max_length=75000)
    category = SortableForeignKey(Category)
    order_for_art = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
