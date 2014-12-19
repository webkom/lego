# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20141218_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abakusgroup',
            name='permission_groups',
            field=models.ManyToManyField(blank=True, null=True, verbose_name='permission groups', to='auth.Group', related_name='abakus_groups'),
            preserve_default=True,
        ),
    ]
