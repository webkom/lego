# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-19 20:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0002_auto_20170903_2206'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='quote',
            options={'ordering': ['created_at']},
        ),
    ]
