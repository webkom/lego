# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-28 10:20
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import lego.apps.files.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tags", "0001_initial"),
        ("companies", "0002_auto_20170828_1020"),
        ("events", "0001_initial"),
        ("files", "0001_initial"),
        ("users", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="registration",
            name="created_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="registration_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="registration",
            name="event",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="registrations",
                to="events.Event",
            ),
        ),
        migrations.AddField(
            model_name="registration",
            name="pool",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="registrations",
                to="events.Pool",
            ),
        ),
        migrations.AddField(
            model_name="registration",
            name="updated_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="registration_updated",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="registration",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="registrations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="pool",
            name="created_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pool_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="pool",
            name="event",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pools",
                to="events.Event",
            ),
        ),
        migrations.AddField(
            model_name="pool",
            name="permission_groups",
            field=models.ManyToManyField(to="users.AbakusGroup"),
        ),
        migrations.AddField(
            model_name="pool",
            name="updated_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pool_updated",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="can_edit_groups",
            field=models.ManyToManyField(
                blank=True, related_name="can_edit_event", to="users.AbakusGroup"
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="can_edit_users",
            field=models.ManyToManyField(
                blank=True, related_name="can_edit_event", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="can_view_groups",
            field=models.ManyToManyField(
                blank=True, related_name="can_view_event", to="users.AbakusGroup"
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="company",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="events",
                to="companies.Company",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="cover",
            field=lego.apps.files.models.FileField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="event_covers",
                to="files.File",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="created_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="event_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="images",
            field=models.ManyToManyField(blank=True, to="files.File"),
        ),
        migrations.AddField(
            model_name="event",
            name="tags",
            field=models.ManyToManyField(blank=True, to="tags.Tag"),
        ),
        migrations.AddField(
            model_name="event",
            name="updated_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="event_updated",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="registration", unique_together=set([("user", "event")])
        ),
    ]
