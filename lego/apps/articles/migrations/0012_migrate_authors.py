# Generated by Django 4.0.9 on 2023-03-16 13:13

from django.conf import settings
from django.db import migrations


def merge_authors(apps, schema_editor):
    Article = apps.get_model("articles", "Article")
    for e in Article.objects.all():
        if e.created_by != None and e.authors.count() == 0:
            e.authors.add(e.created_by)
            e.save()


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("articles", "0011_article_authors"),
    ]

    operations = [
        migrations.RunPython(merge_authors),
    ]
