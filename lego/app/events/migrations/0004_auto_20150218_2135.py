# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20150216_1228'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='merge_date',
            new_name='merge_time',
        ),
    ]
