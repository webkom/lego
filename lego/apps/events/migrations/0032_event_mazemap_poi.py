# Generated by Django 3.0.14 on 2021-11-23 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0031_event_legacy_registration_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='mazemap_poi',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
