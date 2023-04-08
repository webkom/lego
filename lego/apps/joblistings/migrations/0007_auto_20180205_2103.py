# Generated by Django 2.0.2 on 2018-02-05 21:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("joblistings", "0006_joblisting_contact_mail")]

    operations = [
        migrations.AlterField(
            model_name="joblisting",
            name="job_type",
            field=models.CharField(
                choices=[
                    ("full_time", "full_time"),
                    ("part_time", "part_time"),
                    ("summer_job", "summer_job"),
                    ("master_thesis", "master_thesis"),
                    ("other", "other"),
                ],
                max_length=20,
            ),
        )
    ]
