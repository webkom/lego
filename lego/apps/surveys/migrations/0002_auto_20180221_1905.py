# Generated by Django 2.0.2 on 2018-02-21 19:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("surveys", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="survey",
            name="template_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("company_presentation", "company_presentation"),
                    ("lunch_presentation", "lunch_presentation"),
                    ("course", "course"),
                    ("kid_event", "kid_event"),
                    ("party", "party"),
                    ("social", "social"),
                    ("other", "other"),
                    ("event", "event"),
                ],
                max_length=30,
                null=True,
                unique=True,
            ),
        )
    ]
