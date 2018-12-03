from __future__ import unicode_literals
import StringIO
from datetime import datetime

import boto3
from sorl.thumbnail import ImageField, get_thumbnail
import django_countries.fields as countries
import phonenumber_field.modelfields as phonenumber

from django.db import models, transaction
from django.contrib import admin
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage as storage
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from penguin.settings import THUMB_SIZE, AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
s3 = session.resource('s3')

SOLD_CHOICES = (
    ('S','Sold'),
    ('A','For Sale'),
    ('P', 'Pending'),
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

ORDER_STATUS = (
    ('pending', 'Pending'),
    ('ready', 'Ready to Ship'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('confirmed', 'Confirmed')
)

ORDER_METHOD = (
    ('paypal', 'PayPal'),
    ('card', 'Credit Card')
)

CARRIER_CHOICES = (
    ("USPS", "USPS"),
    ("FedEx", "Fedex"),
)

def validate_year(value):
    now = datetime.now()
    thisYear = now.year
    if value < 1800 or value > thisYear:
        raise ValidationError(
            _('%(value)s is outside of the range 1800 to %(year)s'),
            params={'value': value,'year':thisYear},
        )


class OrderManager(models.Manager):
    def validate_create(self, data):
        for field in data:
            if not data[field]:
                return False
        return True

    def update_sold_items(self,items): # this sucks
        with transaction.atomic():
            for item in items:
                if item.in_stock > 1:
                    # if we have multiple of this item available, here we duplicate the item and add it to the database, while marking the original item as sold with quantity 0. hacky
                    pen = getattr(item, 'pen', None)
                    knife = getattr(item, 'knife', None)
                    images = item.image.all()
                    item.pk = None
                    item.in_stock -= 1
                    item.status = 'A'
                    item.order = None
                    item.sold_date = None
                    item.save()
                    if pen:
                        # pen must be duplicated bc one to one relationship 
                        pen.pk = None
                        pen.product = item
                        pen.save()
                        item.pen = pen
                    elif knife:
                        # as with pen
                        knife.pk = None
                        knife.product = item
                        knife.save()
                        item.knife = knife
                    for image in images:
                        # images must be duplicated, as with pen
                        image.pk = None
                        image.product = item
                        image.save()
            current_date = datetime.now().date()
            items.update(status='S', sold_date=current_date, in_stock=0)


class Sale(models.Model):
    def __unicode__(self):
        return self.headline
    headline = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Address(models.Model):
    def __unicode__(self):
        return "{} \n{} {} \n{}, {} {}".format(self.addressee,self.street,self.apt,self.city,self.state,self.zip_code,self.country)
    addressee = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    apt = models.CharField(max_length=12, null=True, blank=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=12)
    country = countries.CountryField(blank_label="Select Country")
    phone = phonenumber.PhoneNumberField()
    email = models.EmailField(max_length=254)


class Order(models.Model):
    def __unicode__(self):
        return "{} order for\n{}\nStatus: {}\nSubtotal: ${}\nShipping: ${}".format(self.order_method.title(), self.shipping_address, self.status, self.subtotal, self.shipping)
    order_method = models.CharField(max_length=10, choices=ORDER_METHOD)
    order_id = models.CharField(max_length=255)
    subtotal = models.DecimalField(max_digits=8,decimal_places=2,validators=[MinValueValidator(0.01)])
    shipping = models.DecimalField(max_digits=8,decimal_places=2,validators=[MinValueValidator(0.01)])
    shipping_address = models.OneToOneField(Address, on_delete=models.CASCADE, related_name="shipping_address")
    shipping_carrier = models.CharField(max_length=25, choices=CARRIER_CHOICES)
    shipping_service = models.CharField(max_length=55)
    status = models.CharField(max_length=10,choices=ORDER_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = OrderManager()


class Product(models.Model):
    def __unicode__(self):
        return "{} {}".format(self.make, self.model)
    make = models.CharField(max_length=55)
    model = models.CharField(max_length=55)
    condition = models.CharField(max_length=25,choices=CONDITIONS)
    flaws = models.CharField(max_length=100)
    special_shipping = models.BooleanField("This item requires special packaging. It will not fit into a USPS flat rate box or FedEx envelope.")
    length = models.DecimalField("Length in inches", max_digits=5,decimal_places=1,validators=[MinValueValidator(0.1)], default=5.0)
    width = models.DecimalField("Width in inches", max_digits=5,decimal_places=1, validators=[MinValueValidator(0.1)], default=1.0, help_text="Please modify width default only if item to be shipped is not a single pen.")
    depth = models.DecimalField("Depth in inches", max_digits=5,decimal_places=1, validators=[MinValueValidator(0.1)], default=1.0, help_text="Please modify depth default only if item to be shipped is not a single pen.")
    weight = models.DecimalField("Weight in ounces", max_digits=5,decimal_places=1,default=3.0,validators=[MinValueValidator(0.1)])
    price = models.DecimalField(max_digits=8,decimal_places=2,validators=[MinValueValidator(0.01)])
    description = models.TextField(max_length=2000)
    purchase_source = models.CharField(max_length=55)
    purchase_date = models.DateField()
    cost = models.DecimalField(max_digits=8,decimal_places=2,validators=[MinValueValidator(0.01)], help_text="If number in stock is more than 1 enter average purchase cost")
    status = models.CharField(max_length=1,choices=SOLD_CHOICES,default='A')
    in_stock = models.IntegerField(default=1, validators=[MinValueValidator(0)], help_text="If number is 0 product must be marked sold.")
    sold_date = models.DateField(blank=True,null=True)
    sale = models.ForeignKey(Sale, related_name='products', blank=True, null=True, on_delete=models.CASCADE)
    order = models.ForeignKey(Order,related_name='products', blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Pen(models.Model):
    product = models.OneToOneField(Product, related_name='pen', on_delete=models.CASCADE)
    year = models.IntegerField(validators=[validate_year])
    country = countries.CountryField(blank=True, null=True)
    cap_color = models.CharField(max_length=25)
    body_color = models.CharField(max_length=25)
    nib_description = models.CharField(max_length=55)
    nib_make = models.CharField(max_length=25)
    nib_grade = models.CharField(max_length=25)
    nib_material = models.CharField(max_length=25)
    nib_flexibility = models.CharField(max_length=25)
    nib_alternative = models.BooleanField()


class Knife(models.Model):
    class Meta:
        verbose_name_plural = "knives"
    product = models.OneToOneField(Product, related_name='knife', on_delete=models.CASCADE)
    knife_type = models.CharField(max_length=25)
    blade_material = models.CharField(max_length=25)
    handle_material = models.CharField(max_length=25)
    blade_length = models.DecimalField(max_digits=4,decimal_places=2)


class Image(models.Model):
    def __unicode__(self):
        return "Image for: {}".format(self.product)
    product = models.ForeignKey(Product, related_name='image', blank=True, null=True, on_delete=models.CASCADE)
    image = ImageField(null=True, upload_to='images')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Bulletin(models.Model):
    def __unicode__(self):
        return "{}".format(self.headline)
    headline = models.CharField(max_length=155)
    text = models.TextField(max_length=75000)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

