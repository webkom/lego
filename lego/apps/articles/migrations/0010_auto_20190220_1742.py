# Generated by Django 2.1.7 on 2019-02-20 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0009_article_youtube_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='youtube_url',
            field=models.URLField(default=''),
        ),
    ]
