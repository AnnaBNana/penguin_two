from __future__ import unicode_literals
from django.db import models
from django.contrib import admin
from tinymce.models import HTMLField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


SOLD_CHOICES = (
    ('S','Sold'),
    ('A','For Sale'),
    ('O', 'On Sale'),
    ('C','Collection'),
)


CONDITIONS = (
    ('mint', 'mint'),
    ('near_mint', 'near mint'),
    ('excellent_plus', 'excellent +'),
    ('excellent', 'excellent'),
    ('very_good_plus', 'very good +'),
    ('very_good', 'very good'),
    ('good', 'good'),
    ('fair', 'fair'),
    ('poor', 'poor'),
)


class Make(models.Model):
    def __unicode__(self):
        return self.maker
    maker = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Nib(models.Model):
    def __unicode__(self):
        return str(self.make) + " " + str(self.model)
    make = models.ForeignKey(Make)
    material = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    style = models.CharField(max_length=255)
    additional_cost = models.DecimalField(max_digits=4,decimal_places=2)
    status = models.CharField(max_length=1,choices=SOLD_CHOICES,default='A')
    sold_date = models.DateField(blank=True,null=True)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Sale(models.Model):
    headline = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Pen(models.Model):
    model = models.CharField(max_length=255)
    year = models.IntegerField()
    condition = models.CharField(max_length=25,choices=CONDITIONS)
    flaws = models.CharField(max_length=255)
    status = models.CharField(max_length=1,choices=SOLD_CHOICES,default='A')
    cap_color = models.CharField(max_length=255)
    body_color = models.CharField(max_length=255)
    length = models.DecimalField(max_digits=4,decimal_places=2)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    cost = models.DecimalField(max_digits=8,decimal_places=2)
    purchase_source = models.CharField(max_length=255)
    purchase_date = models.DateField()
    description = models.TextField(max_length=2000)
    sold_date = models.DateField(blank=True,null=True)
    nib = models.ForeignKey(Nib, related_name="pen")
    sale = models.ForeignKey(Sale,related_name='pen',blank=True,null=True)
    make = models.ForeignKey(Make,related_name='pen')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Knife(models.Model):
    class Meta:
        verbose_name_plural = "knives"
    make = models.ForeignKey(Make,related_name='knife')
    model = models.CharField(max_length=255)
    knife_type = models.CharField(max_length=255)
    blade_material = models.CharField(max_length=255)
    handle_material = models.CharField(max_length=255)
    condition = models.CharField(max_length=25,choices=CONDITIONS)
    length = models.DecimalField(max_digits=4,decimal_places=2)
    blade_length = models.DecimalField(max_digits=4,decimal_places=2)
    status = models.CharField(max_length=1,choices=SOLD_CHOICES,default='A')
    price = models.DecimalField(max_digits=8,decimal_places=2)
    cost = models.DecimalField(max_digits=8,decimal_places=2)
    purchase_source = models.CharField(max_length=255)
    purchase_date = models.DateField()
    description = models.TextField(max_length=2000)
    sold_date = models.DateField(blank=True,null=True)
    sale = models.ForeignKey(Sale,related_name='knife',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Bulletin(models.Model):
    headline = models.CharField(max_length=155)
    text = models.TextField(max_length=2000)
    active = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Image(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type','object_id')
    file = models.ImageField(null=True)
    url = models.CharField(max_length=500,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
