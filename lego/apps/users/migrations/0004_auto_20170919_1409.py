# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-19 14:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20170903_2206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='role',
            field=models.CharField(choices=[('member', 'member'), ('leader', 'leader'), ('co-leader', 'co-leader'), ('treasurer', 'treasurer'), ('recruiting', 'recruiting'), ('development', 'development'), ('editor', 'editor'), ('retiree', 'retiree'), ('media relations', 'media relations'), ('active retiree', 'active retiree'), ('alumni', 'alumni'), ('webmaster', 'webmaster'), ('interest group admin', 'interest group admin'), ('alumni admin', 'alumni admin'), ('vote counter', 'vote counter'), ('retiree email', 'retiree email'), ('company admin', 'company admin'), ('dugnad admin', 'dugnad admin'), ('trip admin', 'trip admin'), ('sponsor admin', 'sponsor admin'), ('social admin', 'social admin')], default='member', max_length=30),
        ),
    ]
