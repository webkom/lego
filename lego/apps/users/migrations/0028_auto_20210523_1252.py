# Generated by Django 2.2.20 on 2021-05-23 12:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0027_auto_20210415_1004"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="selected_theme",
            field=models.CharField(
                choices=[("auto", "auto"), ("light", "light"), ("dark", "dark")],
                default="auto",
                max_length=50,
                verbose_name="selected theme",
            ),
        ),
    ]
