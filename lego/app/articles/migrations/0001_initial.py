# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import basis.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20141113_2313'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('require_auth', models.BooleanField(verbose_name='require auth', default=False)),
                ('title', models.CharField(max_length=255)),
                ('ingress', models.TextField()),
                ('text', models.TextField(blank=True)),
                ('author', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, editable=False)),
                ('can_edit_groups', models.ManyToManyField(to='users.AbakusGroup', null=True, blank=True, related_name='can_edit_article')),
                ('can_edit_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True, related_name='can_edit_article')),
                ('can_view_groups', models.ManyToManyField(to='users.AbakusGroup', null=True, blank=True, related_name='can_view_article')),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='article_created', default=None, editable=False, null=True)),
                ('updated_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='article_updated', default=None, editable=False, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
