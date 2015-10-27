# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mptt.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150826_2000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='abakusgroup',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='abakusgroup',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='abakusgroup',
            name='level',
            field=models.PositiveIntegerField(editable=False, default=1, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='abakusgroup',
            name='lft',
            field=models.PositiveIntegerField(editable=False, default=1, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='abakusgroup',
            name='rght',
            field=models.PositiveIntegerField(editable=False, default=1, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='abakusgroup',
            name='tree_id',
            field=models.PositiveIntegerField(editable=False, default=1, db_index=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='abakusgroup',
            name='parent',
            field=mptt.fields.TreeForeignKey(null=True, related_name='children', blank=True, to='users.AbakusGroup'),
        ),
    ]
