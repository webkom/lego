from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0031_abakusgroup_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="inactive_notified_counter",
            field=models.IntegerField(default=0),
        ),
    ]
