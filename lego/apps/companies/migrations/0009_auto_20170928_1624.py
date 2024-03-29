# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-28 16:24
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations

import lego.apps.files.models


class Migration(migrations.Migration):
    dependencies = [
        ("files", "0002_file_user"),
        ("companies", "0008_merge_20170922_1353"),
    ]

    operations = [
        migrations.AddField(
            model_name="semesterstatus",
            name="evaluation",
            field=lego.apps.files.models.FileField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="semester_status_evaluations",
                to="files.File",
            ),
        ),
        migrations.AddField(
            model_name="semesterstatus",
            name="statistics",
            field=lego.apps.files.models.FileField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="semester_status_statistics",
                to="files.File",
            ),
        ),
        migrations.AlterField(
            model_name="semesterstatus",
            name="contract",
            field=lego.apps.files.models.FileField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="semester_status_contracts",
                to="files.File",
            ),
        ),
    ]
