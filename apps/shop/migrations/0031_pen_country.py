# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-19 04:42
from __future__ import unicode_literals

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0030_auto_20171119_0016'),
    ]

    operations = [
        migrations.AddField(
            model_name='pen',
            name='country',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
        ),
    ]
