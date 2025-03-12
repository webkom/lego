# Generated by Django 4.2.16 on 2025-03-11 13:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0010_reportchangelog"),
    ]

    operations = [
        migrations.AddField(
            model_name="meeting",
            name="is_recurring",
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name="meeting",
            name="is_template",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="meeting",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="children",
                to="meetings.meeting",
            ),
        ),
        migrations.AddIndex(
            model_name="meeting",
            index=models.Index(
                fields=["is_recurring", "is_template", "parent"],
                name="meetings_me_is_recu_cc034c_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="meeting",
            index=models.Index(
                fields=[
                    "created_by",
                    "is_recurring",
                    "is_template",
                    "parent",
                    "start_time",
                ],
                name="meetings_me_created_2229b3_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="meeting",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("is_template", True), ("parent__isnull", False), _negated=True
                ),
                name="prevent_template_with_parent",
            ),
        ),
        migrations.AddConstraint(
            model_name="meeting",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("is_recurring", False), ("is_template", True), _connector="OR"
                ),
                name="recurring_meetings_must_be_templates",
            ),
        ),
    ]
