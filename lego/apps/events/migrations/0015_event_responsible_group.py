# Generated by Django 2.0.2 on 2018-02-23 13:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0015_auto_20180216_2026"),
        ("events", "0014_auto_20180219_1920"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="responsible_group",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="events",
                to="users.AbakusGroup",
            ),
        )
    ]
