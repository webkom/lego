# Generated by Django 2.1.11 on 2019-09-04 17:50

import django.contrib.postgres.fields
from django.db import migrations, models
import lego.apps.users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0007_emaillist_additional_emails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emaillist',
            name='additional_emails',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(default='', error_messages={'unique': 'A user with that email already exists.'}, max_length=254, validators=[lego.apps.users.validators.EmailValidatorWithBlacklist(blacklist=['abakus.no'])]), size=None),
        ),
    ]
