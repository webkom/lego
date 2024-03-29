# Generated by Django 2.1.11 on 2019-09-14 22:22

import django.contrib.postgres.fields
from django.db import migrations, models

import lego.apps.users.validators


class Migration(migrations.Migration):
    dependencies = [("email", "0006_emaillist_require_internal_address")]

    operations = [
        migrations.AddField(
            model_name="emaillist",
            name="additional_emails",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.EmailField(
                    default="",
                    max_length=254,
                    validators=[
                        lego.apps.users.validators.EmailValidatorWithBlacklist(
                            blacklist=["abakus.no"]
                        )
                    ],
                ),
                default=list,
                size=None,
            ),
        )
    ]
