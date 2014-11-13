# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, auto_now_add=True)),
                ('updated_at', models.DateTimeField(default=datetime.datetime.now, auto_now=True)),
                ('title', models.CharField(verbose_name='title', max_length=200)),
                ('slug', models.CharField(db_index=True, unique=True, verbose_name='slug', max_length=100)),
                ('content', models.TextField(verbose_name='content')),
                ('toc', models.BooleanField(default=False, verbose_name='Needs table of contents')),
                ('require_auth', models.BooleanField(default=False, verbose_name='Can only be viewed by authenticated users')),
                ('require_abakom', models.BooleanField(default=False, verbose_name='Can only be viewed by abakom users')),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='page_created', null=True, default=None, editable=False)),
                ('updated_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='page_updated', null=True, default=None, editable=False)),
            ],
            options={
                'verbose_name': 'flatpage',
                'ordering': ('slug',),
                'verbose_name_plural': 'flatpages',
            },
            bases=(models.Model,),
        ),
    ]
