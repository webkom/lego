# Generated by Django 4.2.16 on 2025-03-10 23:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0010_reportchangelog"),
    ]

    operations = [
        migrations.AddField(
            model_name="meeting",
            name="recurring",
            field=models.IntegerField(blank=True, default=-1),
        ),
        migrations.AddIndex(
            model_name="meeting",
            index=models.Index(
                fields=["recurring"], name="meetings_me_recurri_66cf09_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="meeting",
            index=models.Index(
                fields=["created_by", "recurring", "report"],
                name="meetings_me_created_4cb9a2_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="meeting",
            index=models.Index(
                fields=["created_by", "recurring", "report", "start_time"],
                name="meetings_me_created_0203fc_idx",
            ),
        ),
    ]
