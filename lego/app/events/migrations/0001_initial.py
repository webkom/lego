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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('require_auth', models.BooleanField(default=False, verbose_name='require auth')),
                ('title', models.CharField(max_length=255)),
                ('ingress', models.TextField()),
                ('text', models.TextField(blank=True)),
                ('event_type', models.PositiveSmallIntegerField(choices=[(0, 'Company presentation'), (1, 'Course'), (2, 'Party'), (3, 'Other'), (4, 'Event')])),
                ('location', models.CharField(max_length=100)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('merge_time', models.DateTimeField(null=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('can_edit_groups', models.ManyToManyField(blank=True, null=True, related_name='can_edit_event', to='users.AbakusGroup')),
                ('can_edit_users', models.ManyToManyField(blank=True, null=True, related_name='can_edit_event', to=settings.AUTH_USER_MODEL)),
                ('can_view_groups', models.ManyToManyField(blank=True, null=True, related_name='can_view_event', to='users.AbakusGroup')),
                ('created_by', models.ForeignKey(editable=False, default=None, to=settings.AUTH_USER_MODEL, related_name='event_created', null=True)),
                ('updated_by', models.ForeignKey(editable=False, default=None, to=settings.AUTH_USER_MODEL, related_name='event_updated', null=True)),
            ],
            options={
                'ordering': ['start_time'],
            },
        ),
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('name', models.CharField(max_length=100)),
                ('capacity', models.PositiveSmallIntegerField(default=0)),
                ('activation_date', models.DateTimeField()),
                ('created_by', models.ForeignKey(editable=False, default=None, to=settings.AUTH_USER_MODEL, related_name='pool_created', null=True)),
                ('event', models.ForeignKey(to='events.Event', related_name='pools')),
                ('updated_by', models.ForeignKey(editable=False, default=None, to=settings.AUTH_USER_MODEL, related_name='pool_updated', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(editable=False, default=None, to=settings.AUTH_USER_MODEL, related_name='registration_created', null=True)),
                ('event', models.ForeignKey(to='events.Event', related_name='registrations')),
                ('pool', models.ForeignKey(null=True, to='events.Pool', related_name='registrations')),
                ('updated_by', models.ForeignKey(editable=False, default=None, to=settings.AUTH_USER_MODEL, related_name='registration_updated', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='registrations')),
            ],
        ),
        migrations.CreateModel(
            name='WaitingList',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('created_by', models.ForeignKey(editable=False, default=None, to=settings.AUTH_USER_MODEL, related_name='waitinglist_created', null=True)),
                ('event', models.OneToOneField(to='events.Event', related_name='waiting_list')),
                ('updated_by', models.ForeignKey(editable=False, default=None, to=settings.AUTH_USER_MODEL, related_name='waitinglist_updated', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='registration',
            name='waiting_list',
            field=models.ForeignKey(null=True, to='events.WaitingList', related_name='registrations'),
        ),
        migrations.AddField(
            model_name='registration',
            name='waiting_pool',
            field=models.ForeignKey(null=True, to='events.Pool', related_name='waiting_registrations'),
        ),
        migrations.AlterUniqueTogether(
            name='registration',
            unique_together=set([('user', 'pool')]),
        ),
    ]
