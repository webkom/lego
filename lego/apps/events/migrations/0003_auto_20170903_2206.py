# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-03 22:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("events", "0002_auto_20170828_1020")]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="require_auth",
            field=models.BooleanField(default=True),
        )
    ]
