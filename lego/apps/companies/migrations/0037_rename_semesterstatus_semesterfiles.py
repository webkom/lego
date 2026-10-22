import django.db.models.deletion
from django.db import migrations, models

import lego.apps.files.models


class Migration(migrations.Migration):
    dependencies = [
        ("companies", "0036_remove_company_active"),
        ("files", "0005_file_save_for_use"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="semesterstatus",
            name="contacted_status",
        ),
        migrations.RenameModel(
            old_name="SemesterStatus",
            new_name="SemesterFiles",
        ),
        migrations.AlterField(
            model_name="semesterfiles",
            name="company",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="semester_files",
                to="companies.company",
            ),
        ),
        migrations.AlterField(
            model_name="semesterfiles",
            name="contract",
            field=lego.apps.files.models.FileField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="semester_contracts",
                to="files.file",
            ),
        ),
        migrations.AlterField(
            model_name="semesterfiles",
            name="statistics",
            field=lego.apps.files.models.FileField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="semester_statistics",
                to="files.file",
            ),
        ),
        migrations.AlterField(
            model_name="semesterfiles",
            name="evaluation",
            field=lego.apps.files.models.FileField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="semester_evaluations",
                to="files.file",
            ),
        ),
    ]
