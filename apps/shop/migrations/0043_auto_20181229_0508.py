# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-12-29 05:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0042_auto_20171226_0652'),
    ]

    operations = [
        migrations.CreateModel(
            name='VacationMode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('headline', models.CharField(max_length=155)),
                ('message', models.TextField(max_length=75000)),
                ('end_date', models.DateField()),
                ('active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterField(
            model_name='bulletin',
            name='text',
            field=models.TextField(max_length=75000),
        ),
    ]