# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-09 20:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_user_allergies'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('male', 'male'), ('female', 'female'), ('other', 'other')], default='male', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='membership',
            name='role',
            field=models.CharField(choices=[('member', 'member'), ('leader', 'leader'), ('co-leader', 'co-leader'), ('treasurer', 'treasurer')], default='member', max_length=20),
        ),
    ]
