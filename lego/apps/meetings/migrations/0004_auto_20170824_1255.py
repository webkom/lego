# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-24 12:55
from __future__ import unicode_literals

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0003_meeting_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='deleted',
            field=models.BooleanField(db_index=True, default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='meetinginvitation',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False),
        ),
        migrations.AlterField(
            model_name='meetinginvitation',
            name='deleted',
            field=models.BooleanField(db_index=True, default=False, editable=False),
        ),
    ]
