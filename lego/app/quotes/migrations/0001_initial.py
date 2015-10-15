# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import basis.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0002_auto_20150826_2000'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('require_auth', models.BooleanField(default=False, verbose_name='require auth')),
                ('title', models.CharField(max_length=255)),
                ('quote', models.TextField()),
                ('source', models.CharField(max_length=255)),
                ('approved', models.BooleanField(default=False)),
                ('likes', models.PositiveIntegerField()),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('can_edit_groups', models.ManyToManyField(to='users.AbakusGroup', blank=True, related_name='can_edit_quote', null=True)),
                ('can_edit_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True, related_name='can_edit_quote', null=True)),
                ('can_view_groups', models.ManyToManyField(to='users.AbakusGroup', blank=True, related_name='can_view_quote', null=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='quote_created', editable=False, default=None, null=True)),
                ('updated_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='quote_updated', editable=False, default=None, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
