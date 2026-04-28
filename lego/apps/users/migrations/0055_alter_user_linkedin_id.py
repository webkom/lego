from django.db import migrations, models

import lego.apps.users.validators
import lego.utils.validators


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0054_alter_user_first_name_alter_user_last_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="linkedin_id",
            field=models.CharField(
                blank=True,
                help_text="Enter a valid LinkedIn ID.",
                max_length=200,
                null=True,
                validators=[
                    lego.apps.users.validators.linkedin_id_validator,
                    lego.utils.validators.ReservedNameValidator(),
                ],
            ),
        ),
    ]
