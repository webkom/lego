# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-15 17:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reactions', '0002_auto_20161025_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reactiontype',
            name='short_code',
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
    ]
