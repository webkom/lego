# Generated by Django 2.1.7 on 2019-03-25 19:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("joblistings", "0007_auto_20180205_2103")]

    operations = [
        migrations.AddField(
            model_name="joblisting",
            name="youtube_url",
            field=models.URLField(
                blank=True,
                default="",
                validators=[
                    django.core.validators.RegexValidator(
                        regex="(^(?:https?:\\/\\/)?(?:www[.])?(?:youtube[.]com\\/watch[?]v=|youtu[.]be\\/))"
                    )
                ],
            ),
        )
    ]
