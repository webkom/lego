# Generated by Django 2.0.3 on 2018-04-06 17:30

from django.db import migrations

import lego.apps.content.fields


class Migration(migrations.Migration):
    dependencies = [("flatpages", "0003_auto_20171210_1610")]

    operations = [
        migrations.AlterField(
            model_name="page",
            name="content",
            field=lego.apps.content.fields.ContentField(allow_images=False),
        )
    ]
