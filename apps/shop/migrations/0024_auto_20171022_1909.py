# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-22 19:09
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0023_address_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='weight',
            field=models.DecimalField(decimal_places=1, default=3, max_digits=5, validators=[django.core.validators.MinValueValidator(0.1)]),
        ),
    ]
