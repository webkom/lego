# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-01 16:02
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models

import lego.apps.users.managers


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_merge_20170427_1812'),
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
            name='username',
            field=models.CharField(db_index=True, error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=30, unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.  This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')]),
        ),
    ]
