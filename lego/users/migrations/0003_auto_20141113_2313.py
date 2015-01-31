# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20141107_2218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abakusgroup',
            name='parent',
            field=models.ForeignKey(verbose_name='parent', related_name='children', blank=True, null=True, to='users.AbakusGroup'),
            preserve_default=True,
        ),
    ]
