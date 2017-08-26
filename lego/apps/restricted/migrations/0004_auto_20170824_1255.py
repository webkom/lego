# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-24 12:55
from __future__ import unicode_literals

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restricted', '0003_auto_20170524_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restrictedmail',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False),
        ),
        migrations.AlterField(
            model_name='restrictedmail',
            name='deleted',
            field=models.BooleanField(db_index=True, default=False, editable=False),
        ),
    ]
