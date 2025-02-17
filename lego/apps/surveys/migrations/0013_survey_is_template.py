from django.db import migrations, models


def set_is_template(apps, schema_editor):
    Survey = apps.get_model("surveys", "Survey")
    Survey.objects.filter(template_type__isnull=False).update(is_template=True)


class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0012_alter_survey_template_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="survey",
            name="is_template",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(set_is_template),
    ]
