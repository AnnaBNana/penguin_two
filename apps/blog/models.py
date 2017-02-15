from __future__ import unicode_literals
from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField(max_length=75000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
