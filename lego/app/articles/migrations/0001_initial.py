# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import basis.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150826_2000'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('require_auth', models.BooleanField(default=False, verbose_name='require auth')),
                ('title', models.CharField(max_length=255)),
                ('ingress', models.TextField()),
                ('text', models.TextField(blank=True)),
                ('slug', models.SlugField(unique=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('can_edit_groups', models.ManyToManyField(null=True, blank=True, to='users.AbakusGroup', related_name='can_edit_article')),
                ('can_edit_users', models.ManyToManyField(null=True, blank=True, to=settings.AUTH_USER_MODEL, related_name='can_edit_article')),
                ('can_view_groups', models.ManyToManyField(null=True, blank=True, to='users.AbakusGroup', related_name='can_view_article')),
                ('created_by', models.ForeignKey(related_name='article_created', default=None, null=True, to=settings.AUTH_USER_MODEL, editable=False)),
                ('updated_by', models.ForeignKey(related_name='article_updated', default=None, null=True, to=settings.AUTH_USER_MODEL, editable=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
