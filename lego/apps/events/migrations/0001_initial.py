# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-28 10:20
from __future__ import unicode_literals

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Event",
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
                (
                    "require_auth",
                    models.BooleanField(default=False, verbose_name="require auth"),
                ),
                ("slug", models.SlugField(null=True, unique=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("text", models.TextField(blank=True)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("company_presentation", "company_presentation"),
                            ("lunch_presentation", "lunch_presentation"),
                            ("course", "course"),
                            ("kid_event", "kid_event"),
                            ("party", "party"),
                            ("social", "social"),
                            ("other", "other"),
                            ("event", "event"),
                        ],
                        max_length=50,
                    ),
                ),
                ("location", models.CharField(max_length=100)),
                ("start_time", models.DateTimeField(db_index=True)),
                ("end_time", models.DateTimeField()),
                ("merge_time", models.DateTimeField(null=True)),
                ("penalty_weight", models.PositiveIntegerField(default=1)),
                (
                    "penalty_weight_on_not_present",
                    models.PositiveIntegerField(default=2),
                ),
                ("heed_penalties", models.BooleanField(default=True)),
                ("use_captcha", models.BooleanField(default=True)),
                ("feedback_required", models.BooleanField(default=False)),
                ("is_priced", models.BooleanField(default=False)),
                ("use_stripe", models.BooleanField(default=True)),
                ("price_member", models.PositiveIntegerField(default=0)),
                ("price_guest", models.PositiveIntegerField(default=0)),
                ("payment_due_date", models.DateTimeField(null=True)),
                ("payment_overdue_notified", models.BooleanField(default=False)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Pool",
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
                ("name", models.CharField(max_length=100)),
                ("capacity", models.PositiveSmallIntegerField(default=0)),
                ("activation_date", models.DateTimeField()),
                ("unregistration_deadline", models.DateTimeField(null=True)),
            ],
            options={"abstract": False, "default_manager_name": "objects"},
        ),
        migrations.CreateModel(
            name="Registration",
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
                (
                    "registration_date",
                    models.DateTimeField(auto_now_add=True, db_index=True),
                ),
                ("unregistration_date", models.DateTimeField(null=True)),
                ("feedback", models.CharField(blank=True, max_length=100)),
                ("admin_reason", models.CharField(blank=True, max_length=100)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING_REGISTER", "PENDING_REGISTER"),
                            ("SUCCESS_REGISTER", "SUCCESS_REGISTER"),
                            ("FAILURE_REGISTER", "FAILURE_REGISTER"),
                            ("PENDING_UNREGISTER", "PENDING_UNREGISTER"),
                            ("SUCCESS_UNREGISTER", "SUCCESS_UNREGISTER"),
                            ("FAILURE_UNREGISTER", "FAILURE_UNREGISTER"),
                        ],
                        default="PENDING_REGISTER",
                        max_length=20,
                    ),
                ),
                (
                    "presence",
                    models.CharField(
                        choices=[
                            ("UNKNOWN", "UNKNOWN"),
                            ("PRESENT", "PRESENT"),
                            ("NOT_PRESENT", "NOT_PRESENT"),
                        ],
                        default="UNKNOWN",
                        max_length=20,
                    ),
                ),
                ("charge_id", models.CharField(max_length=50, null=True)),
                ("charge_amount", models.IntegerField(default=0)),
                ("charge_amount_refunded", models.IntegerField(default=0)),
                ("charge_status", models.CharField(max_length=50, null=True)),
                ("last_notified_overdue_payment", models.DateTimeField(null=True)),
            ],
            options={"ordering": ["registration_date"]},
        ),
    ]
