# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-14 11:58
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0002_auto_20170714_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gallerypicture',
            name='gallery',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pictures', to='gallery.Gallery'),
        ),
    ]
