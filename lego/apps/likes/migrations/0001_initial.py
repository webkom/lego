# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-21 11:42
from __future__ import unicode_literals

import basis.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('users', '0002_auto_20160622_1517'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('require_auth', models.BooleanField(default=False, verbose_name='require auth')),
                ('object_id', models.PositiveIntegerField()),
                ('can_edit_groups', models.ManyToManyField(blank=True, related_name='can_edit_like', to='users.AbakusGroup')),
                ('can_edit_users', models.ManyToManyField(blank=True, related_name='can_edit_like', to=settings.AUTH_USER_MODEL)),
                ('can_view_groups', models.ManyToManyField(blank=True, related_name='can_view_like', to='users.AbakusGroup')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='like_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='like_updated', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together=set([('user', 'content_type', 'object_id')]),
        ),
    ]
