# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='role',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='role',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='abakusgroup',
            name='is_committee',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='role',
        ),
        migrations.DeleteModel(
            name='Role',
        ),
        migrations.AddField(
            model_name='membership',
            name='title',
            field=models.CharField(default='Member', blank=True, verbose_name='role', max_length=30),
            preserve_default=True,
        ),
    ]
