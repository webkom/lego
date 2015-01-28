# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import basis.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0004_auto_20150116_2248'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('require_auth', models.BooleanField(verbose_name='require auth', default=False)),
                ('title', models.CharField(max_length=255)),
                ('ingress', models.TextField()),
                ('text', models.TextField(blank=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('can_edit_groups', models.ManyToManyField(null=True, related_name='can_edit_article', blank=True, to='users.AbakusGroup')),
                ('can_edit_users', models.ManyToManyField(null=True, related_name='can_edit_article', blank=True, to=settings.AUTH_USER_MODEL)),
                ('can_view_groups', models.ManyToManyField(null=True, related_name='can_view_article', blank=True, to='users.AbakusGroup')),
                ('created_by', models.ForeignKey(null=True, related_name='article_created', default=None, editable=False, to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, related_name='article_updated', default=None, editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
