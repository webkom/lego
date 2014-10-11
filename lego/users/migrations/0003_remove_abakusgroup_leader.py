# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20141009_2233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='abakusgroup',
            name='leader',
        ),
    ]
