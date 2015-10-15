# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0004_auto_20151008_1856'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quote',
            name='likes',
        ),
    ]
