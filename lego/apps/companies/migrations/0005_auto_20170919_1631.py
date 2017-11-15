# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-19 16:31
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models

import lego.apps.files.models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0002_file_user'),
        ('companies', '0004_auto_20170907_1336'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyFile',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    )
                ),
            ],
        ),
        migrations.AddField(
            model_name='company',
            name='logo',
            field=lego.apps.files.models.FileField(
                null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='company_logos', to='files.File'
            ),
        ),
        migrations.AddField(
            model_name='semesterstatus',
            name='contract',
            field=lego.apps.files.models.FileField(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to='files.File'
            ),
        ),
        migrations.AddField(
            model_name='companyfile',
            name='company',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='files',
                to='companies.Company'
            ),
        ),
        migrations.AddField(
            model_name='companyfile',
            name='file',
            field=lego.apps.files.models.FileField(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to='files.File'
            ),
        ),
    ]
