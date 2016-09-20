# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-20 18:46
from __future__ import unicode_literals

import basis.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('require_auth', models.BooleanField(default=False, verbose_name='require auth')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('slug', models.CharField(db_index=True, max_length=100, unique=True, verbose_name='slug')),
                ('content', models.TextField(verbose_name='content')),
                ('toc', models.BooleanField(default=False, verbose_name='Needs table of contents')),
                ('can_edit_groups', models.ManyToManyField(blank=True, related_name='can_edit_page', to='users.AbakusGroup')),
                ('can_edit_users', models.ManyToManyField(blank=True, related_name='can_edit_page', to=settings.AUTH_USER_MODEL)),
                ('can_view_groups', models.ManyToManyField(blank=True, related_name='can_view_page', to='users.AbakusGroup')),
                ('created_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='page_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='page_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'flatpage',
                'verbose_name_plural': 'flatpages',
                'ordering': ('slug',),
            },
        ),
    ]
