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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('require_auth', models.BooleanField(default=False, verbose_name='require auth')),
                ('title', models.CharField(max_length=255)),
                ('text', models.TextField()),
                ('source', models.CharField(max_length=255)),
                ('approved', models.BooleanField(default=False)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('can_edit_groups', models.ManyToManyField(to='users.AbakusGroup', blank=True, related_name='can_edit_quote', null=True)),
                ('can_edit_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True, related_name='can_edit_quote', null=True)),
                ('can_view_groups', models.ManyToManyField(to='users.AbakusGroup', blank=True, related_name='can_view_quote', null=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, default=None, editable=False, related_name='quote_created', null=True)),
                ('updated_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, default=None, editable=False, related_name='quote_updated', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QuoteLike',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('like_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, default=None, editable=False, related_name='quotelike_created', null=True)),
                ('quote', models.ForeignKey(to='quotes.Quote')),
                ('updated_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, default=None, editable=False, related_name='quotelike_updated', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='quotelike',
            unique_together=set([('user', 'quote')]),
        ),
    ]
