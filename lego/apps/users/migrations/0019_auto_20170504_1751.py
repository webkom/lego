# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-04 17:51
from __future__ import unicode_literals

from django.db import migrations, models
import lego.apps.users.managers


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_user_student_username'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', lego.apps.users.managers.AbakusUserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(error_messages={'unique': 'A user with that email already exists.'}, max_length=254, unique=True),
        ),
    ]
