# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_merge'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='registration',
            unique_together=set([('user', 'event')]),
        ),
    ]
