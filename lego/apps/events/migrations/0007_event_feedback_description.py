# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-18 10:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("events", "0006_merge_20171004_2216")]

    operations = [
        migrations.AddField(
            model_name="event",
            name="feedback_description",
            field=models.CharField(blank=True, max_length=255),
        )
    ]
