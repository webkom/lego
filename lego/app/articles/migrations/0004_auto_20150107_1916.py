# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0003_auto_20141119_1626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='can_edit_groups',
            field=models.ManyToManyField(null=True, to='users.AbakusGroup', blank=True, related_name='can_edit_article'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='article',
            name='can_edit_users',
            field=models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL, blank=True, related_name='can_edit_article'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='article',
            name='can_view_groups',
            field=models.ManyToManyField(null=True, to='users.AbakusGroup', blank=True, related_name='can_view_article'),
            preserve_default=True,
        ),
    ]
