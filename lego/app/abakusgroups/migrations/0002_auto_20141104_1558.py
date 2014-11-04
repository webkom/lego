# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abakusgroups', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='membership',
            old_name='abakusgroup',
            new_name='abakus_group',
        ),
        migrations.AlterField(
            model_name='abakusgroup',
            name='permission_groups',
            field=models.ManyToManyField(blank=True, related_query_name='abakus_groups', related_name='abakus_groups', verbose_name='permission groups', to='auth.Group'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([('user', 'abakus_group')]),
        ),
    ]
