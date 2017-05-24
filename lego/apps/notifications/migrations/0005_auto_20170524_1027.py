# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-24 10:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0004_auto_20170427_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationsetting',
            name='notification_type',
            field=models.CharField(choices=[('weekly_mail', 'weekly_mail'), ('event_bump', 'event_bump'), ('event_admin_registration', 'event_admin_registration'), ('event_payment_overdue', 'event_payment_overdue'), ('meeting_invite', 'meeting_invite'), ('penalty_creation', 'penalty_creation'), ('restricted_mail_sent', 'restricted_mail_sent')], max_length=64),
        ),
    ]
