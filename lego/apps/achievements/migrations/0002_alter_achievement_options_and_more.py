# Generated by Django 4.2.16 on 2024-11-04 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("achievements", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="achievement",
            options={},
        ),
        migrations.AddIndex(
            model_name="achievement",
            index=models.Index(
                fields=["user", "identifier", "level"],
                name="achievement_user_id_58535a_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="achievement",
            constraint=models.UniqueConstraint(
                fields=("user", "identifier"), name="unique_user_identifier"
            ),
        ),
    ]