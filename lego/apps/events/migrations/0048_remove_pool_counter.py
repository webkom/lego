from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0047_alter_event_event_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pool",
            name="counter",
        ),
    ]
