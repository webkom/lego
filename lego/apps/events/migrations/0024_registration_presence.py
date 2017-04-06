# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-06 18:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0023_auto_20170324_1810'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='presence',
            field=models.CharField(choices=[('UNKNOWN', 'UNKNOWN'), ('PRESENT', 'PRESENT'), ('NOT_PRESENT', 'NOT_PRESENT')], default='UNKNOWN', max_length=20),
        ),
    ]
