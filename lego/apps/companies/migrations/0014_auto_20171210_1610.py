# Generated by Django 2.0 on 2017-12-10 16:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("companies", "0013_merge_20171015_1132")]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="created_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="company_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="student_contact",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="companies",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="updated_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="company_updated",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="companycontact",
            name="created_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="companycontact_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="companycontact",
            name="updated_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="companycontact_updated",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="semester",
            name="created_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="semester_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="semester",
            name="updated_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="semester_updated",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
