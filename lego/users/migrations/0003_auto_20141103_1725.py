# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20141031_1236'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='membership',
            name='permission_status',
        ),
        migrations.AddField(
            model_name='membership',
            name='is_active',
            field=models.BooleanField(verbose_name='is active', default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='membership',
            name='role',
            field=models.CharField(verbose_name='role', max_length=2, default='M', choices=[('M', 'Member'), ('L', 'Leader'), ('CL', 'Co-Leader'), ('T', 'Treasurer')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(verbose_name='groups', blank=True, to='users.AbakusGroup', related_query_name='user', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', through='users.Membership', related_name='users'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(verbose_name='user permissions', blank=True, to='auth.Permission', related_query_name='user', help_text='Specific permissions for this user.', related_name='users'),
            preserve_default=True,
        ),
    ]
