# Generated by Django 4.2.16 on 2024-12-28 23:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("companies", "0030_alter_company_options"),
    ]

    operations = [
        migrations.RenameField(
            model_name="studentcompanycontact",
            old_name="student",
            new_name="user",
        ),
    ]
