# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import basis.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quotes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LikeList',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('quote', models.PositiveIntegerField()),
                ('like_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, default=None, editable=False, to=settings.AUTH_USER_MODEL, related_name='likelist_created')),
                ('updated_by', models.ForeignKey(null=True, default=None, editable=False, to=settings.AUTH_USER_MODEL, related_name='likelist_updated')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='likelist',
            unique_together=set([('user', 'quote')]),
        ),
    ]
