# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-28 10:20
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
        ('events', '0002_auto_20170828_1020'),
        ('meetings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    )
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now, editable=False
                    )
                ),
                (
                    'updated_at',
                    models.DateTimeField(default=django.utils.timezone.now, editable=False)
                ),
                ('deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('message', models.TextField()),
                ('sent', models.DateTimeField(default=None, null=True)),
                (
                    'created_by',
                    models.ForeignKey(
                        default=None, editable=False, null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='announcement_created', to=settings.AUTH_USER_MODEL
                    )
                ),
                ('events', models.ManyToManyField(blank=True, to='events.Event')),
                ('groups', models.ManyToManyField(blank=True, to='users.AbakusGroup')),
                ('meetings', models.ManyToManyField(blank=True, to='meetings.Meeting')),
                (
                    'updated_by',
                    models.ForeignKey(
                        default=None, editable=False, null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='announcement_updated', to=settings.AUTH_USER_MODEL
                    )
                ),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'default_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='NotificationSetting',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    )
                ),
                (
                    'notification_type',
                    models.CharField(
                        choices=[
                            ('weekly_mail', 'weekly_mail'), ('event_bump', 'event_bump'),
                            ('event_admin_registration', 'event_admin_registration'),
                            ('event_payment_overdue',
                             'event_payment_overdue'), ('meeting_invite', 'meeting_invite'),
                            ('penalty_creation',
                             'penalty_creation'), ('restricted_mail_sent', 'restricted_mail_sent'),
                            ('announcement', 'announcement')
                        ], max_length=64
                    )
                ),
                ('enabled', models.BooleanField(default=True)),
                (
                    'channels',
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[('email', 'email'), ('push', 'push')], max_length=64
                        ), default=['email', 'push'], null=True, size=None
                    )
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    )
                ),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='notificationsetting',
            unique_together=set([('user', 'notification_type')]),
        ),
    ]
