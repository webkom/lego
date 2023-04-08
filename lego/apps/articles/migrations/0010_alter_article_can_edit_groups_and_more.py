# Generated by Django 4.0.6 on 2022-07-26 11:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("users", "0033_alter_abakusgroup_type"),
        ("articles", "0009_article_youtube_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="can_edit_groups",
            field=models.ManyToManyField(
                blank=True, related_name="can_edit_%(class)s", to="users.abakusgroup"
            ),
        ),
        migrations.AlterField(
            model_name="article",
            name="can_edit_users",
            field=models.ManyToManyField(
                blank=True,
                related_name="can_edit_%(class)s",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="article",
            name="can_view_groups",
            field=models.ManyToManyField(
                blank=True, related_name="can_view_%(class)s", to="users.abakusgroup"
            ),
        ),
        migrations.AlterField(
            model_name="article",
            name="created_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)s_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="article",
            name="updated_by",
            field=models.ForeignKey(
                default=None,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)s_updated",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
