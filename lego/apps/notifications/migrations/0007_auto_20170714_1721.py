# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-14 17:21
from __future__ import unicode_literals

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0026_auto_20170504_1019'),
        ('meetings', '0003_meeting_images'),
        ('users', '0018_user_student_username'),
        ('notifications', '0006_auto_20170703_1741'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('message', models.TextField()),
                ('created_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='announcement_created', to=settings.AUTH_USER_MODEL)),
                ('events', models.ManyToManyField(blank=True, to='events.Event')),
                ('groups', models.ManyToManyField(blank=True, to='users.AbakusGroup')),
                ('meetings', models.ManyToManyField(blank=True, to='meetings.Meeting')),
                ('updated_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='announcement_updated', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'default_manager_name': 'objects',
            },
        ),
        migrations.AlterField(
            model_name='notificationsetting',
            name='notification_type',
            field=models.CharField(choices=[('weekly_mail', 'weekly_mail'), ('event_bump', 'event_bump'), ('event_admin_registration', 'event_admin_registration'), ('event_payment_overdue', 'event_payment_overdue'), ('meeting_invite', 'meeting_invite'), ('penalty_creation', 'penalty_creation'), ('restricted_mail_sent', 'restricted_mail_sent'), ('announcement', 'announcement')], max_length=64),
        ),
    ]
