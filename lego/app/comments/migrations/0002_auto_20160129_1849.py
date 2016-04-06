# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-29 18:49
from __future__ import unicode_literals

import basis.models
import django.db.models.deletion
import django.db.models.manager
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20151105_2217'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='comment',
            managers=[
                ('public_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.RemoveField(
            model_name='comment',
            name='content',
        ),
        migrations.AddField(
            model_name='comment',
            name='can_edit_groups',
            field=models.ManyToManyField(blank=True, null=True, related_name='can_edit_comment', to='users.AbakusGroup'),
        ),
        migrations.AddField(
            model_name='comment',
            name='can_edit_users',
            field=models.ManyToManyField(blank=True, null=True, related_name='can_edit_comment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='can_view_groups',
            field=models.ManyToManyField(blank=True, null=True, related_name='can_view_comment', to='users.AbakusGroup'),
        ),
        migrations.AddField(
            model_name='comment',
            name='created_at',
            field=models.DateTimeField(default=basis.models._now, editable=False),
        ),
        migrations.AddField(
            model_name='comment',
            name='created_by',
            field=models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='ingress',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='require_auth',
            field=models.BooleanField(default=False, verbose_name='require auth'),
        ),
        migrations.AddField(
            model_name='comment',
            name='text',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='title',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='updated_at',
            field=models.DateTimeField(default=basis.models._now, editable=False),
        ),
        migrations.AddField(
            model_name='comment',
            name='updated_by',
            field=models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_updated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
