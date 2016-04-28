# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import basis.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150826_2000'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('require_auth', models.BooleanField(default=False, verbose_name='require auth')),
                ('title', models.CharField(max_length=255)),
                ('ingress', models.TextField()),
                ('text', models.TextField(blank=True)),
                ('slug', models.SlugField(unique=True)),
                ('event_type', models.PositiveSmallIntegerField(choices=[(0, 'Company presentation'), (1, 'Course'), (2, 'Party'), (3, 'Other'), (4, 'Event')])),
                ('location', models.CharField(max_length=100)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('merge_time', models.DateTimeField(null=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('can_edit_groups', models.ManyToManyField(null=True, blank=True, to='users.AbakusGroup', related_name='can_edit_event')),
                ('can_edit_users', models.ManyToManyField(null=True, blank=True, to=settings.AUTH_USER_MODEL, related_name='can_edit_event')),
                ('can_view_groups', models.ManyToManyField(null=True, blank=True, to='users.AbakusGroup', related_name='can_view_event')),
                ('created_by', models.ForeignKey(related_name='event_created', default=None, null=True, to=settings.AUTH_USER_MODEL, editable=False)),
                ('updated_by', models.ForeignKey(related_name='event_updated', default=None, null=True, to=settings.AUTH_USER_MODEL, editable=False)),
            ],
            options={
                'ordering': ['start_time'],
            },
        ),
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('name', models.CharField(max_length=100)),
                ('capacity', models.PositiveSmallIntegerField(default=0)),
                ('activation_date', models.DateTimeField()),
                ('created_by', models.ForeignKey(related_name='pool_created', default=None, null=True, to=settings.AUTH_USER_MODEL, editable=False)),
                ('event', models.ForeignKey(to='events.Event', related_name='pools')),
                ('permission_groups', models.ManyToManyField(to='users.AbakusGroup')),
                ('updated_by', models.ForeignKey(related_name='pool_updated', default=None, null=True, to=settings.AUTH_USER_MODEL, editable=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(related_name='registration_created', default=None, null=True, to=settings.AUTH_USER_MODEL, editable=False)),
                ('event', models.ForeignKey(to='events.Event', related_name='registrations')),
                ('pool', models.ForeignKey(related_name='registrations', null=True, to='events.Pool')),
                ('updated_by', models.ForeignKey(related_name='registration_updated', default=None, null=True, to=settings.AUTH_USER_MODEL, editable=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='registrations')),
            ],
        ),
        migrations.CreateModel(
            name='WaitingList',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('created_by', models.ForeignKey(related_name='waitinglist_created', default=None, null=True, to=settings.AUTH_USER_MODEL, editable=False)),
                ('event', models.OneToOneField(related_name='waiting_list', to='events.Event')),
                ('updated_by', models.ForeignKey(related_name='waitinglist_updated', default=None, null=True, to=settings.AUTH_USER_MODEL, editable=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='registration',
            name='waiting_list',
            field=models.ForeignKey(related_name='registrations', null=True, to='events.WaitingList'),
        ),
        migrations.AddField(
            model_name='registration',
            name='waiting_pool',
            field=models.ForeignKey(related_name='waiting_registrations', null=True, to='events.Pool'),
        ),
        migrations.AlterUniqueTogether(
            name='registration',
            unique_together=set([('user', 'pool')]),
        ),
    ]
