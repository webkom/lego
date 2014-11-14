# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='can_view',
        ),
        migrations.RemoveField(
            model_name='article',
            name='groups_can_edit',
        ),
        migrations.RemoveField(
            model_name='article',
            name='users_can_edit',
        ),
    ]
