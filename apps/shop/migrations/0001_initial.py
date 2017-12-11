# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-06-29 17:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bulletin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('headline', models.CharField(max_length=155)),
                ('text', models.TextField(max_length=2000)),
                ('active', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('image', sorl.thumbnail.fields.ImageField(null=True, upload_to='images')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Knife',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(max_length=255)),
                ('knife_type', models.CharField(max_length=255)),
                ('blade_material', models.CharField(max_length=255)),
                ('handle_material', models.CharField(max_length=255)),
                ('condition', models.CharField(choices=[('mint', 'mint'), ('near_mint', 'near mint'), ('excellent_plus', 'excellent +'), ('excellent', 'excellent'), ('very_good_plus', 'very good +'), ('very_good', 'very good'), ('good', 'good'), ('fair', 'fair'), ('poor', 'poor')], max_length=25)),
                ('length', models.DecimalField(decimal_places=2, max_digits=4)),
                ('blade_length', models.DecimalField(decimal_places=2, max_digits=4)),
                ('status', models.CharField(choices=[('S', 'Sold'), ('A', 'For Sale'), ('P', 'Pending'), ('O', 'On Sale'), ('C', 'Collection')], default='A', max_length=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('purchase_source', models.CharField(max_length=255)),
                ('purchase_date', models.DateField()),
                ('description', models.TextField(max_length=2000)),
                ('sold_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'knives',
            },
        ),
        migrations.CreateModel(
            name='Make',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('maker', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_cost', models.CharField(max_length=10)),
                ('status', models.CharField(choices=[('P', 'Pending'), ('R', 'Ready to Ship'), ('S', 'Shipped'), ('D', 'Delivered'), ('C', 'Confirmed')], max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(max_length=255)),
                ('year', models.IntegerField()),
                ('condition', models.CharField(choices=[('mint', 'mint'), ('near_mint', 'near mint'), ('excellent_plus', 'excellent +'), ('excellent', 'excellent'), ('very_good_plus', 'very good +'), ('very_good', 'very good'), ('good', 'good'), ('fair', 'fair'), ('poor', 'poor')], max_length=25)),
                ('flaws', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('S', 'Sold'), ('A', 'For Sale'), ('P', 'Pending'), ('O', 'On Sale'), ('C', 'Collection')], default='A', max_length=1)),
                ('cap_color', models.CharField(max_length=255)),
                ('body_color', models.CharField(max_length=255)),
                ('length', models.DecimalField(decimal_places=2, max_digits=4)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('purchase_source', models.CharField(max_length=255)),
                ('purchase_date', models.DateField()),
                ('description', models.TextField(max_length=2000)),
                ('sold_date', models.DateField(blank=True, null=True)),
                ('nib_description', models.CharField(max_length=255)),
                ('nib_make', models.CharField(max_length=255)),
                ('nib_grade', models.CharField(max_length=255)),
                ('nib_style', models.CharField(max_length=255)),
                ('nib_material', models.CharField(max_length=255)),
                ('nib_flexibility', models.CharField(max_length=255)),
                ('nib_alternative', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('make', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pen', to='shop.Make')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product', to='shop.Order')),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('headline', models.TextField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='pen',
            name='sale',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pen', to='shop.Sale'),
        ),
        migrations.AddField(
            model_name='knife',
            name='make',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='knife', to='shop.Make'),
        ),
        migrations.AddField(
            model_name='knife',
            name='sale',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='knife', to='shop.Sale'),
        ),
    ]
