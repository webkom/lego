# Generated by Django 4.0.10 on 2024-03-05 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lending', '0005_remove_lendinginstance_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='lendinginstance',
            name='comment',
            field=models.TextField(blank=True),
        ),
    ]