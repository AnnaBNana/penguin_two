# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-01 02:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0016_auto_20171001_0204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='depth',
            field=models.DecimalField(decimal_places=1, max_digits=5),
        ),
    ]
