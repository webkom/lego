from django.apps import apps
from django.db import migrations, models


def populate_achievements_score(apps, schema_editor):
    from lego.apps.achievements.utils.calculation_utils import calculate_user_rank

    User = apps.get_model("users", "User")

    for user in User.objects.all():
        user.achievements_score = calculate_user_rank(user)
        user.save(update_fields=["achievements_score"])


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0044_alter_membership_role_alter_membershiphistory_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="achievements_score",
            field=models.FloatField(default=0),
        ),
        migrations.RunPython(populate_achievements_score),
    ]
