# Generated by Django 4.0.10 on 2023-11-21 19:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("joblistings", "0009_alter_joblisting_created_by_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="joblisting",
            name="visible_from",
            field=models.DateTimeField(),
        ),
    ]