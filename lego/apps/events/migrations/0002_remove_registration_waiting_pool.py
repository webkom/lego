# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-09-05 20:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registration',
            name='waiting_pool',
        ),
    ]
