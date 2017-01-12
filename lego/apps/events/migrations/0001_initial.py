# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-28 17:05
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=timezone.now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('require_auth', models.BooleanField(default=False, verbose_name='require auth')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('text', models.TextField(blank=True)),
                ('slug', models.SlugField(null=True, unique=True)),
                ('event_type', models.PositiveSmallIntegerField(choices=[(0, 'Company presentation'), (1, 'Course'), (2, 'Party'), (3, 'Other'), (4, 'Event')])),
                ('location', models.CharField(max_length=100)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('merge_time', models.DateTimeField(null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('can_edit_groups', models.ManyToManyField(blank=True, related_name='can_edit_event', to='users.AbakusGroup')),
                ('can_edit_users', models.ManyToManyField(blank=True, related_name='can_edit_event', to=settings.AUTH_USER_MODEL)),
                ('can_view_groups', models.ManyToManyField(blank=True, related_name='can_view_event', to='users.AbakusGroup')),
                ('created_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['start_time'],
            },
        ),
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=timezone.now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('name', models.CharField(max_length=100)),
                ('capacity', models.PositiveSmallIntegerField(default=0)),
                ('activation_date', models.DateTimeField()),
                ('created_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pool_created', to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pools', to='events.Event')),
                ('permission_groups', models.ManyToManyField(to='users.AbakusGroup')),
                ('updated_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pool_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=timezone.now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('unregistration_date', models.DateTimeField(null=True)),
                ('created_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registration_created', to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='events.Event')),
                ('pool', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='events.Pool')),
                ('updated_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registration_updated', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to=settings.AUTH_USER_MODEL)),
                ('waiting_pool', models.ManyToManyField(null=True, related_name='waiting_registrations', to='events.Pool')),
            ],
            options={
                'ordering': ['registration_date'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='registration',
            unique_together=set([('user', 'event')]),
        ),
    ]
