# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models

import lego.permissions.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20151027_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abakusgroup',
            name='permissions',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(validators=[lego.permissions.validators.KeywordPermissionValidator()], max_length=30), default=list, size=None, verbose_name='permissions'),
        ),
    ]
