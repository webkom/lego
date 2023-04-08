# Generated by Django 2.1.5 on 2019-01-28 19:14

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("companies", "0015_auto_20181001_1801")]

    operations = [
        migrations.AlterField(
            model_name="companyinterest",
            name="events",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    choices=[
                        ("company_presentation", "company_presentation"),
                        ("course", "course"),
                        ("lunch_presentation", "lunch_presentation"),
                        ("bedex", "bedex"),
                        ("other", "other"),
                        ("sponsor", "sponsor"),
                        ("start_up", "start_up"),
                    ],
                    max_length=64,
                ),
                size=None,
            ),
        )
    ]
