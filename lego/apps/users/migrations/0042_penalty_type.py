# Generated by Django 4.0.10 on 2024-03-14 10:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0041_user_linkedin_id_alter_user_github_username"),
    ]

    operations = [
        migrations.AddField(
            model_name="penalty",
            name="type",
            field=models.CharField(
                choices=[
                    ("presence", "Presence"),
                    ("payment", "Payment"),
                    ("other", "Other"),
                ],
                default="other",
                max_length=50,
            ),
        ),
    ]