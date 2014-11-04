# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20141104_1553'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='groups',
            new_name='abakus_groups',
        ),
    ]
