# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2020-06-08 01:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0047_auto_20200608_0127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='shop.Address'),
        ),
    ]
