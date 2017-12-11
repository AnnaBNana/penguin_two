# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-21 04:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_auto_20170921_0402'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='country',
            field=models.CharField(default='USA', max_length=55),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='address',
            name='zip_code',
            field=models.CharField(max_length=12),
        ),
    ]
