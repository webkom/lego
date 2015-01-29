# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name_plural': 'users', 'verbose_name': 'user', 'permissions': (('retrieve_user', 'Can retrieve user'), ('list_user', 'Can list users'))},
        ),
        migrations.AlterUniqueTogether(
            name='abakusgroup',
            unique_together=set([('name',)]),
        ),
    ]
