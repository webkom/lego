# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-28 10:20
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("users", "0001_initial"),
        ("comments", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="can_edit_groups",
            field=models.ManyToManyField(
                blank=True, related_name="can_edit_comment", to="users.AbakusGroup"
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="can_edit_users",
            field=models.ManyToManyField(
                blank=True, related_name="can_edit_comment", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="can_view_groups",
            field=models.ManyToManyField(
                blank=True, related_name="can_view_comment", to="users.AbakusGroup"
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="content_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.ContentType",
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="created_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comment_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="comments.Comment",
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="updated_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comment_updated",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
