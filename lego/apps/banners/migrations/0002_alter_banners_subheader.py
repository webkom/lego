# Generated by Django 4.2.16 on 2025-03-07 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("banners", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="banners",
            name="subheader",
            field=models.CharField(max_length=256, null=True),
        ),
    ]
