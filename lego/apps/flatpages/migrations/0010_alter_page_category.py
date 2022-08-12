# Generated by Django 3.2.14 on 2022-08-12 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("flatpages", "0009_auto_20200915_0823"),
    ]

    operations = [
        migrations.AlterField(
            model_name="page",
            name="category",
            field=models.CharField(
                choices=[
                    ("generelt", "generelt"),
                    ("organisasjon", "organisasjon"),
                    ("styrer", "styrer"),
                    ("bedrifter", "bedrifter"),
                    ("arrangementer", "arrangementer"),
                    ("grupper", "grupper"),
                    ("utnevnelser", "utnevnelser"),
                    ("personvern", "personvern"),
                ],
                default="generelt",
                max_length=50,
            ),
        ),
    ]
