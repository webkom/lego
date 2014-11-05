# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import basis.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('ingress', models.TextField(verbose_name='ingress')),
                ('text', models.TextField(verbose_name='article text')),
                ('author', models.ForeignKey(verbose_name='author', to=settings.AUTH_USER_MODEL, editable=False, null=True)),
                ('can_edit', models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='editable_articleeditasble_articles')),
                ('created_by', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, default=None, null=True, related_name='article_created')),
                ('updated_by', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, default=None, null=True, related_name='article_updated')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
