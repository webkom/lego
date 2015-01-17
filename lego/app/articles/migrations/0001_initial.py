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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('require_auth', models.BooleanField(verbose_name='require auth', default=False)),
                ('title', models.CharField(max_length=255)),
                ('ingress', models.TextField()),
                ('text', models.TextField(blank=True)),
                ('author', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, editable=False)),
                ('can_edit_groups', models.ManyToManyField(blank=True, null=True, related_name='can_edit_article', to='users.AbakusGroup')),
                ('can_edit_users', models.ManyToManyField(blank=True, null=True, related_name='can_edit_article', to=settings.AUTH_USER_MODEL)),
                ('can_view_groups', models.ManyToManyField(blank=True, null=True, related_name='can_view_article', to='users.AbakusGroup')),
                ('created_by', models.ForeignKey(related_name='article_created', default=None, null=True, to=settings.AUTH_USER_MODEL, editable=False)),
                ('updated_by', models.ForeignKey(related_name='article_updated', default=None, null=True, to=settings.AUTH_USER_MODEL, editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
