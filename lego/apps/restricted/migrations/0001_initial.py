# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-28 10:20
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
        ('events', '0002_auto_20170828_1020'),
        ('meetings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RestrictedMail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('from_address', models.EmailField(db_index=True, max_length=254)),
                ('hide_sender', models.BooleanField(default=False)),
                ('token', models.CharField(db_index=True, max_length=128, unique=True)),
                ('used', models.DateTimeField(null=True)),
                ('raw_addresses', django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), null=True, size=None)),
                ('created_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='restrictedmail_created', to=settings.AUTH_USER_MODEL)),
                ('events', models.ManyToManyField(blank=True, to='events.Event')),
                ('groups', models.ManyToManyField(blank=True, to='users.AbakusGroup')),
                ('meetings', models.ManyToManyField(blank=True, to='meetings.Meeting')),
                ('updated_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='restrictedmail_updated', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'default_manager_name': 'objects',
            },
        ),
    ]
