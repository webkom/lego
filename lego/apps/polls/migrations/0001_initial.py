# Generated by Django 2.1.5 on 2019-01-17 19:00

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import lego.apps.content.fields
import lego.apps.polls.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tags", "0003_auto_20170908_1732"),
    ]

    operations = [
        migrations.CreateModel(
            name="Option",
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
                ("name", models.CharField(max_length=30)),
                ("votes", models.IntegerField(default=0)),
                (
                    "created_by",
                    models.ForeignKey(
                        default=None,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="option_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-votes", "pk"]},
        ),
        migrations.CreateModel(
            name="Poll",
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
                ("text", lego.apps.content.fields.ContentField(allow_images=False)),
                ("pinned", models.BooleanField(default=False)),
                ("description", models.TextField(blank=True)),
                (
                    "valid_until",
                    models.DateTimeField(default=lego.apps.polls.models.get_time_delta),
                ),
                (
                    "answered_users",
                    models.ManyToManyField(
                        related_name="answered_polls", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        default=None,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="poll_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("tags", models.ManyToManyField(blank=True, to="tags.Tag")),
                (
                    "updated_by",
                    models.ForeignKey(
                        default=None,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="poll_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"get_latest_by": "created_at"},
        ),
        migrations.AddField(
            model_name="option",
            name="poll",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="options",
                to="polls.Poll",
            ),
        ),
        migrations.AddField(
            model_name="option",
            name="updated_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="option_updated",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
