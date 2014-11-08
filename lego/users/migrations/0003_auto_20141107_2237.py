# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20141031_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', through='users.Membership', to='users.AbakusGroup', related_query_name='user', related_name='users', blank=True, verbose_name='groups'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(help_text='Specific permissions for this user.', to='auth.Permission', related_query_name='user', related_name='users', blank=True, verbose_name='user permissions'),
            preserve_default=True,
        ),
    ]
