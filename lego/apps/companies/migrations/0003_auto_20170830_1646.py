# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-30 16:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("companies", "0002_auto_20170828_1020")]

    operations = [
        migrations.AlterModelOptions(name="company", options={}),
        migrations.AlterModelOptions(name="companycontact", options={}),
        migrations.AlterModelOptions(name="companyinterest", options={}),
        migrations.AddField(
            model_name="companycontact",
            name="public",
            field=models.BooleanField(default=False),
        ),
    ]
