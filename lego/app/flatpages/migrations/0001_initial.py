# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import basis.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('slug', models.CharField(verbose_name='slug', db_index=True, unique=True, max_length=100)),
                ('content', models.TextField(verbose_name='content')),
                ('toc', models.BooleanField(default=False, verbose_name='Needs table of contents')),
                ('require_auth', models.BooleanField(default=False, verbose_name='Can only be viewed by authenticated users')),
                ('require_abakom', models.BooleanField(default=False, verbose_name='Can only be viewed by abakom users')),
                ('created_by', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, null=True, related_name='page_created', default=None)),
                ('updated_by', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, null=True, related_name='page_updated', default=None)),
            ],
            options={
                'verbose_name': 'flatpage',
                'ordering': ('slug',),
                'verbose_name_plural': 'flatpages',
            },
            bases=(models.Model,),
        ),
    ]
