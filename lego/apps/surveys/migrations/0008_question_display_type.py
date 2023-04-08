# Generated by Django 2.1.11 on 2020-02-21 20:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("surveys", "0007_auto_20190714_1906")]

    operations = [
        migrations.AddField(
            model_name="question",
            name="display_type",
            field=models.CharField(
                choices=[("pie_chart", "pie_chart"), ("bar_chart", "bar_chart")],
                default="pie_chart",
                max_length=64,
            ),
        )
    ]
