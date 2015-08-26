# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models

import lego.permissions.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abakusgroup',
            name='permissions',
            field=django.contrib.postgres.fields.ArrayField(verbose_name='permissions', size=None, null=True, base_field=models.CharField(validators=[lego.permissions.validators.KeywordPermissionValidator()], max_length=30)),
        ),
    ]
