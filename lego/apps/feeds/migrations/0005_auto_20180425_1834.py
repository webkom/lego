# Generated by Django 2.0.4 on 2018-04-25 18:34

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0004_auto_20180425_1530'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notificationfeed',
            name='read_at',
        ),
        migrations.RemoveField(
            model_name='notificationfeed',
            name='seen_at',
        ),
        migrations.AlterField(
            model_name='notificationfeed',
            name='activity_store',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=[]),
        ),
        migrations.AlterField(
            model_name='personalfeed',
            name='activity_store',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=[]),
        ),
        migrations.AlterField(
            model_name='userfeed',
            name='activity_store',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=[]),
        ),
    ]
