# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sorttype',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='sorttype',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='quote',
            name='publish_date',
        ),
        migrations.DeleteModel(
            name='SortType',
        ),
    ]
