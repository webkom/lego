# Generated by Django 2.0.2 on 2018-02-07 16:11

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("comments", "0005_auto_20171210_1610")]

    operations = [
        migrations.RemoveField(model_name="comment", name="can_edit_groups"),
        migrations.RemoveField(model_name="comment", name="can_edit_users"),
        migrations.RemoveField(model_name="comment", name="can_view_groups"),
        migrations.RemoveField(model_name="comment", name="require_auth"),
    ]
