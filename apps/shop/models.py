from __future__ import unicode_literals
from PIL import Image as Img
import StringIO

import boto3

from django.db import models
from django.contrib import admin
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage as storage
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile

from penguin.settings import THUMB_SIZE, AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
s3 = session.resource('s3')

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


class Image(models.Model):
    def image_thumb(self):
        return mark_safe('<img src="{}" width="100" height="100" />'.format(self.file.url))
    def __unicode__(self):
        return "Image for: {}".format(self.content_object.__unicode__())
    image_thumb.short_description = 'Image'
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type','object_id')
    file = models.ImageField(null=True, upload_to='images')
    thumb = models.ImageField(upload_to='thumbs', editable=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        super(Image, self).save(*args, **kwargs)
        if not self.thumb:
            self.make_thumb()
        print "save executed"
    def make_thumb(self):
        img = Img.open(storage.open(self.file.name))
        img.thumbnail(THUMB_SIZE)
        thumb_io = StringIO.StringIO()
        img.save(thumb_io, format='JPEG')
        thumb_file = InMemoryUploadedFile(thumb_io, None, "thumb_" + self.file.name, 'image/jpeg',thumb_io.len, None)
        self.thumb = thumb_file
        self.save(update_fields=['thumb'])


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
    def __unicode__(self):
        return "{} {} {} {}".format(self.year, self.body_color, self.make, self.model)
    make = models.ForeignKey(Make,related_name='pen')
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
    images = GenericRelation(Image)
    sale = models.ForeignKey(Sale,related_name='pen',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Knife(models.Model):
    class Meta:
        verbose_name_plural = "knives"
    def __unicode__(self):
        return "{} {} {} {}".format(self.make, self.model, self.knife_type)
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
    images = GenericRelation(Image)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Bulletin(models.Model):
    headline = models.CharField(max_length=155)
    text = models.TextField(max_length=2000)
    active = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
