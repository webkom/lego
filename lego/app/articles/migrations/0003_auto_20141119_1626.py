# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0003_auto_20141113_2313'),
        ('articles', '0002_auto_20141114_2304'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='can_edit_groups',
            field=models.ManyToManyField(related_name='can_edit_article', to='users.AbakusGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='can_edit_users',
            field=models.ManyToManyField(related_name='can_edit_article', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='can_view_groups',
            field=models.ManyToManyField(related_name='can_view_article', to='users.AbakusGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='require_auth',
            field=models.BooleanField(verbose_name='require auth', default=False),
            preserve_default=True,
        ),
    ]
