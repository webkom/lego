# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import basis.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0003_auto_20141113_2313'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('ingress', models.TextField(verbose_name='ingress')),
                ('text', models.TextField(verbose_name='article text', blank=True)),
                ('author', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, editable=False, verbose_name='author')),
                ('can_view', models.ManyToManyField(to='users.AbakusGroup', related_name='viewable_articles')),
                ('created_by', models.ForeignKey(related_name='article_created', null=True, to=settings.AUTH_USER_MODEL, editable=False, default=None)),
                ('groups_can_edit', models.ManyToManyField(to='users.AbakusGroup', related_name='editable_articles')),
                ('updated_by', models.ForeignKey(related_name='article_updated', null=True, to=settings.AUTH_USER_MODEL, editable=False, default=None)),
                ('users_can_edit', models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='editable_articles')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
