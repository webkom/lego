# Generated by Django 2.1.2 on 2018-10-10 16:30

import django.contrib.postgres.fields
from django.db import migrations, models

import lego.apps.permissions.validators


class Migration(migrations.Migration):
    dependencies = [("users", "0018_auto_20180827_1746")]

    operations = [
        migrations.AlterField(
            model_name="abakusgroup",
            name="permissions",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    max_length=50,
                    validators=[
                        lego.apps.permissions.validators.KeywordPermissionValidator()
                    ],
                ),
                default=list,
                size=None,
                verbose_name="permissions",
            ),
        )
    ]
