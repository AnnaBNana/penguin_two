# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-26 02:04
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0039_product_in_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='in_stock',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]