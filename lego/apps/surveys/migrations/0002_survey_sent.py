# Generated by Django 2.0.2 on 2018-02-26 21:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("surveys", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="survey", name="sent", field=models.BooleanField(default=False)
        )
    ]
