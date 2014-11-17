# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20141113_2313'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('flatpages', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='require_abakom',
        ),
        migrations.AddField(
            model_name='page',
            name='can_edit_groups',
            field=models.ManyToManyField(to='users.AbakusGroup', related_name='can_edit_page'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='can_edit_users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='can_edit_page'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='can_view_groups',
            field=models.ManyToManyField(to='users.AbakusGroup', related_name='can_view_page'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='require_auth',
            field=models.BooleanField(default=False, verbose_name='require auth'),
            preserve_default=True,
        ),
    ]
