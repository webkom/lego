# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-12 18:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
        ('events', '0017_auto_20161207_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='tags',
            field=models.ManyToManyField(blank=True, to='tags.Tag'),
        ),
    ]
