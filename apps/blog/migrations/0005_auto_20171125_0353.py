# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-25 03:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20171120_0429'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='intro',
            options={'verbose_name': 'Statement of Purpose', 'verbose_name_plural': 'Statements of Purpose'},
        ),
    ]
