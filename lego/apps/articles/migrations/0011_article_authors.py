# Generated by Django 4.0.9 on 2023-03-16 13:13

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("articles", "0010_alter_article_can_edit_groups_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="authors",
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]