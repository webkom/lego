# Generated by Django 4.0.10 on 2023-10-31 17:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0037_event_responsible_users"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="is_foreign_language",
            field=models.BooleanField(default=False),
        ),
    ]
