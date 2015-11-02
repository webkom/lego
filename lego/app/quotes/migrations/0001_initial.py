# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import basis.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0002_auto_20150826_2000'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('require_auth', models.BooleanField(default=False, verbose_name='require auth')),
                ('title', models.CharField(max_length=255)),
                ('quote', models.TextField()),
                ('source', models.CharField(max_length=255)),
                ('approved', models.BooleanField(default=False)),
                ('publish_date', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('can_edit_groups', models.ManyToManyField(related_name='can_edit_quote', null=True, to='users.AbakusGroup', blank=True)),
                ('can_edit_users', models.ManyToManyField(related_name='can_edit_quote', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
                ('can_view_groups', models.ManyToManyField(related_name='can_view_quote', null=True, to='users.AbakusGroup', blank=True)),
                ('created_by', models.ForeignKey(related_name='quote_created', to=settings.AUTH_USER_MODEL, default=None, null=True, editable=False)),
                ('updated_by', models.ForeignKey(related_name='quote_updated', to=settings.AUTH_USER_MODEL, default=None, null=True, editable=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QuoteLike',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('like_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(related_name='quotelike_created', to=settings.AUTH_USER_MODEL, default=None, null=True, editable=False)),
                ('quote', models.ForeignKey(to='quotes.Quote')),
                ('updated_by', models.ForeignKey(related_name='quotelike_updated', to=settings.AUTH_USER_MODEL, default=None, null=True, editable=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SortType',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('created_by', models.ForeignKey(related_name='sorttype_created', to=settings.AUTH_USER_MODEL, default=None, null=True, editable=False)),
                ('updated_by', models.ForeignKey(related_name='sorttype_updated', to=settings.AUTH_USER_MODEL, default=None, null=True, editable=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='quotelike',
            unique_together=set([('user', 'quote')]),
        ),
    ]
