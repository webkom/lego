# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='membership',
            old_name='title',
            new_name='role',
        ),
        migrations.AlterField(
            model_name='membership',
            name='end_date',
            field=models.DateField(blank=True, null=True, verbose_name='end date'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='start_date',
            field=models.DateField(verbose_name='start date', auto_now=True),
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([('user', 'group')]),
        ),
    ]
