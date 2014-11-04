# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20141103_1725'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='abakusgroup',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='abakusgroup',
            name='permissions',
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='membership',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='group',
        ),
        migrations.DeleteModel(
            name='AbakusGroup',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='user',
        ),
        migrations.DeleteModel(
            name='Membership',
        ),
        migrations.RemoveField(
            model_name='user',
            name='user_permissions',
        ),
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, related_query_name='user', to='abakusgroups.AbakusGroup', verbose_name='abakus groups', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='users', through='abakusgroups.Membership'),
            preserve_default=True,
        ),
    ]
