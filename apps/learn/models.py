from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Category(models.Model):
    class Meta:
        verbose_name_plural = "categories"
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Article(models.Model):
    headline = models.CharField(max_length=255)
    text = models.TextField(max_length=75000)
    category = models.ForeignKey(Category, related_name='article')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
