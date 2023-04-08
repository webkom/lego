# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-28 23:35
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models

import lego.utils.validators


class Migration(migrations.Migration):
    dependencies = [("users", "0004_abakusgroup_logo")]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(
                blank=True, max_length=50, verbose_name="first name"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                db_index=True,
                error_messages={"unique": "A user with that username already exists."},
                help_text="Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.",
                max_length=50,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        "^[\\w.@+-]+$",
                        "Enter a valid username.  This value may contain only letters, numbers and @/./+/-/_ characters.",
                        "invalid",
                    ),
                    lego.utils.validators.ReservedNameValidator(),
                ],
            ),
        ),
    ]
