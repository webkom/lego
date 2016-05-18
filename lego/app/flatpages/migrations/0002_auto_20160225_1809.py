# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-25 18:09
from __future__ import unicode_literals

import django.db.models.manager
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flatpages', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='page',
            managers=[
                ('public_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterField(
            model_name='page',
            name='can_edit_groups',
            field=models.ManyToManyField(blank=True, related_name='can_edit_page', to='users.AbakusGroup'),
        ),
        migrations.AlterField(
            model_name='page',
            name='can_edit_users',
            field=models.ManyToManyField(blank=True, related_name='can_edit_page', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='page',
            name='can_view_groups',
            field=models.ManyToManyField(blank=True, related_name='can_view_page', to='users.AbakusGroup'),
        ),
    ]
