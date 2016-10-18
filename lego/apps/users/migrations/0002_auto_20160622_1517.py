# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-22 15:17
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models

import lego.apps.permissions.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abakusgroup',
            name='permissions',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50, validators=[lego.apps.permissions.validators.KeywordPermissionValidator()]), default=list, size=None, verbose_name='permissions'),
        ),
    ]
