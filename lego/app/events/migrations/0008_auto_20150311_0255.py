# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_registration_event'),
    ]

    operations = [
        migrations.RenameField(
            model_name='registration',
            old_name='waiting_pool',
            new_name='waiting_pools',
        ),
    ]
