# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-12 17:53
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0010_auto_20170930_1336'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companyinterest',
            name='collaboration',
        ),
        migrations.RemoveField(
            model_name='companyinterest',
            name='itdagene',
        ),
        migrations.RemoveField(
            model_name='companyinterest',
            name='readme',
        ),
        migrations.AddField(
            model_name='companyinterest',
            name='other_offers',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('collaboration', 'collaboration'), ('readme', 'readme'), ('itdagene', 'itdagene'), ('labamba_sponsor', 'labamba_sponsor')], max_length=64), default=[], size=None),
            preserve_default=False,
        ),
    ]
