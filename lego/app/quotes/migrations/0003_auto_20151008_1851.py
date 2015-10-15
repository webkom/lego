# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import basis.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quotes', '0002_auto_20151008_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuoteLike',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('quote', models.PositiveIntegerField()),
                ('like_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='quotelike_created', default=None, null=True, editable=False)),
                ('updated_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='quotelike_updated', default=None, null=True, editable=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='likelist',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='likelist',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='likelist',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='likelist',
            name='user',
        ),
        migrations.DeleteModel(
            name='LikeList',
        ),
        migrations.AlterUniqueTogether(
            name='quotelike',
            unique_together=set([('user', 'quote')]),
        ),
    ]
