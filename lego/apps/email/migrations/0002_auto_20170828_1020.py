# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-28 10:20
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("email", "0001_initial"),
        ("users", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="emaillist",
            name="groups",
            field=models.ManyToManyField(
                blank=True, related_name="email_lists", to="users.AbakusGroup"
            ),
        ),
        migrations.AddField(
            model_name="emaillist",
            name="users",
            field=models.ManyToManyField(
                blank=True, related_name="email_lists", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
