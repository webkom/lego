# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-01 19:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_auto_20161025_2051'),
    ]

    operations = [
        migrations.AddField(
            model_name='pool',
            name='unregistration_deadline',
            field=models.DateTimeField(null=True),
        ),
    ]
