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
        ("files", "0001_initial"),
        ("users", "0001_initial"),
        ("articles", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="can_edit_groups",
            field=models.ManyToManyField(
                blank=True, related_name="can_edit_article", to="users.AbakusGroup"
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="can_edit_users",
            field=models.ManyToManyField(
                blank=True, related_name="can_edit_article", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="can_view_groups",
            field=models.ManyToManyField(
                blank=True, related_name="can_view_article", to="users.AbakusGroup"
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="cover",
            field=lego.apps.files.models.FileField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="article_covers",
                to="files.File",
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="created_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="article_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="images",
            field=models.ManyToManyField(blank=True, to="files.File"),
        ),
        migrations.AddField(
            model_name="article",
            name="tags",
            field=models.ManyToManyField(blank=True, to="tags.Tag"),
        ),
        migrations.AddField(
            model_name="article",
            name="updated_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="article_updated",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
