# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import basis.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0003_auto_20141113_2313'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('require_auth', models.BooleanField(default=False, verbose_name='require auth')),
                ('title', models.CharField(max_length=255)),
                ('ingress', models.TextField()),
                ('text', models.TextField(blank=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, null=True)),
                ('can_edit_groups', models.ManyToManyField(to='users.AbakusGroup', blank=True, null=True, related_name='can_edit_article')),
                ('can_edit_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True, null=True, related_name='can_edit_article')),
                ('can_view_groups', models.ManyToManyField(to='users.AbakusGroup', blank=True, null=True, related_name='can_view_article')),
                ('created_by', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, editable=False, null=True, related_name='article_created')),
                ('updated_by', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, editable=False, null=True, related_name='article_updated')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
