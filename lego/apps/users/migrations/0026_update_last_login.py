from django.db import migrations
from django.utils import timezone


def update_login(apps, schema_editor):
    UserModel = apps.get_model("users", "User")
    UserModel.objects.all().update(last_login=timezone.now())


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0025_user_phone_number"),
    ]

    operations = [
        migrations.RunPython(update_login),
    ]
