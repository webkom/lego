# Generated by Django 2.2.9 on 2020-02-25 16:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("followers", "0002_auto_20170831_1103")]

    operations = [
        migrations.AddField(
            model_name="followevent",
            name="sent",
            field=models.BooleanField(default=False),
        )
    ]
