from __future__ import unicode_literals
from django.db import models

# Create your models here.
class Post(models.Model):
    def __unicode__(self):
        return self.title
    title = models.CharField(max_length=255)
    text = models.TextField(max_length=75000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Intro(models.Model):
    class Meta:
        verbose_name = 'Statement of Purpose'
        verbose_name_plural = 'Statements of Purpose'
    def __unicode__(self):
        return self.title
    title = models.CharField(max_length=255)
    text = models.TextField(max_length=1200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)