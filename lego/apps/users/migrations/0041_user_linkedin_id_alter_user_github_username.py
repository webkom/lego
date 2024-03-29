# Generated by Django 4.0.10 on 2023-08-31 19:40

import django.core.validators
from django.db import migrations, models

import lego.utils.validators


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0040_user_student_verification_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="linkedin_id",
            field=models.CharField(
                help_text="Enter a valid LinkedIn ID.",
                max_length=71,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        "^[a-zA-Z0-9-]{0,70}$", "Enter a valid LinkedIn ID."
                    ),
                    lego.utils.validators.ReservedNameValidator(),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="github_username",
            field=models.CharField(
                help_text="Enter a valid username.",
                max_length=39,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        "^[a-zA-Z\\d](?:[a-zA-Z\\d]|-(?=[a-zA-Z\\d])){0,38}$",
                        "Enter a valid GitHub username.",
                    ),
                    lego.utils.validators.ReservedNameValidator(),
                ],
            ),
        ),
    ]
