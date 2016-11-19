# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-18 12:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_pool_unregistration_deadline'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='registration',
            options={'ordering': ['registration_date']},
        ),
        migrations.AlterField(
            model_name='registration',
            name='registration_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
