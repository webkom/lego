# Generated by Django 2.0.2 on 2018-02-23 16:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("events", "0015_event_responsible_group")]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="responsible_group",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="events",
                to="users.AbakusGroup",
            ),
        )
    ]
