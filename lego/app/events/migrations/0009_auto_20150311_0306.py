# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_auto_20150311_0255'),
    ]

    operations = [
        migrations.RenameField(
            model_name='registration',
            old_name='waiting_pools',
            new_name='waiting_pool',
        ),
        migrations.RemoveField(
            model_name='registration',
            name='possible_pools',
        ),
    ]
