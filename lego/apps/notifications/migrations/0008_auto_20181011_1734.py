# Generated by Django 2.1.2 on 2018-10-11 17:34

import django.contrib.postgres.fields
from django.db import migrations, models

import lego.apps.notifications.models


class Migration(migrations.Migration):
    dependencies = [("notifications", "0007_auto_20180226_2130")]

    operations = [
        migrations.AlterField(
            model_name="notificationsetting",
            name="channels",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    choices=[("email", "email"), ("push", "push")], max_length=64
                ),
                default=lego.apps.notifications.models._default_channels,
                null=True,
                size=None,
            ),
        )
    ]
