# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_auto_20150311_0307'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pool',
            old_name='size',
            new_name='capacity',
        ),
    ]
