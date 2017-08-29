# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-28 10:20
from __future__ import unicode_literals

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('key', models.CharField(max_length=200, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator('^[\\w-]+\\.[A-Za-z]{2,4}$', 'enter a valid key', 'invalid')])),
                ('state', models.CharField(choices=[('pending_upload', 'pending_upload'), ('ready', 'ready')], default='pending_upload', max_length=24)),
                ('file_type', models.CharField(choices=[('image', 'image'), ('document', 'document')], max_length=24)),
                ('token', models.CharField(max_length=32)),
                ('public', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
