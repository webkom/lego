# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('flatpages', '0002_auto_20141114_2213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='can_edit_groups',
            field=models.ManyToManyField(blank=True, null=True, to='users.AbakusGroup', related_name='can_edit_page'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='can_edit_users',
            field=models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL, related_name='can_edit_page'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='can_view_groups',
            field=models.ManyToManyField(blank=True, null=True, to='users.AbakusGroup', related_name='can_view_page'),
            preserve_default=True,
        ),
    ]
