# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import basis.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('require_auth', models.BooleanField(verbose_name='require auth', default=False)),
                ('title', models.CharField(verbose_name='title', max_length=200)),
                ('slug', models.CharField(db_index=True, unique=True, max_length=100, verbose_name='slug')),
                ('content', models.TextField(verbose_name='content')),
                ('toc', models.BooleanField(verbose_name='Needs table of contents', default=False)),
                ('can_edit_groups', models.ManyToManyField(blank=True, to='users.AbakusGroup', null=True, related_name='can_edit_page')),
                ('can_edit_users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, null=True, related_name='can_edit_page')),
                ('can_view_groups', models.ManyToManyField(blank=True, to='users.AbakusGroup', null=True, related_name='can_view_page')),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='page_created', default=None, editable=False)),
                ('updated_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='page_updated', default=None, editable=False)),
            ],
            options={
                'verbose_name': 'flatpage',
                'verbose_name_plural': 'flatpages',
                'ordering': ('slug',),
            },
        ),
    ]
