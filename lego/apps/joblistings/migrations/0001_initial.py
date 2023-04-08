# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-28 10:20
from __future__ import unicode_literals

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tags", "0001_initial"),
        ("files", "0002_file_user"),
        ("companies", "0002_auto_20170828_1020"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Joblisting",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now, editable=False
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                (
                    "deleted",
                    models.BooleanField(db_index=True, default=False, editable=False),
                ),
                ("slug", models.SlugField(null=True, unique=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("text", models.TextField(blank=True)),
                ("deadline", models.DateTimeField(null=True)),
                ("visible_from", models.DateTimeField(auto_now_add=True)),
                ("visible_to", models.DateTimeField()),
                (
                    "job_type",
                    models.CharField(
                        choices=[
                            ("full_time", "full_time"),
                            ("part_time", "part_time"),
                            ("summer_job", "summer_job"),
                            ("other", "other"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "from_year",
                    models.PositiveIntegerField(
                        choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default="1"
                    ),
                ),
                (
                    "to_year",
                    models.PositiveIntegerField(
                        choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default="5"
                    ),
                ),
                ("application_url", models.URLField(blank=True, null=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="joblistings",
                        to="companies.Company",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        default=None,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="joblisting_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("images", models.ManyToManyField(blank=True, to="files.File")),
                (
                    "responsible",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="joblistings",
                        to="companies.CompanyContact",
                    ),
                ),
                ("tags", models.ManyToManyField(blank=True, to="tags.Tag")),
                (
                    "updated_by",
                    models.ForeignKey(
                        default=None,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="joblisting_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Workplace",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now, editable=False
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                (
                    "deleted",
                    models.BooleanField(db_index=True, default=False, editable=False),
                ),
                ("town", models.CharField(max_length=100)),
                (
                    "created_by",
                    models.ForeignKey(
                        default=None,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="workplace_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        default=None,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="workplace_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False, "default_manager_name": "objects"},
        ),
        migrations.AddField(
            model_name="joblisting",
            name="workplaces",
            field=models.ManyToManyField(to="joblistings.Workplace"),
        ),
    ]
