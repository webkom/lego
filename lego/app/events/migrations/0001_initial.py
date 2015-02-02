# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import basis.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0004_auto_20150116_2248'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('require_auth', models.BooleanField(default=False, verbose_name='require auth')),
                ('title', models.CharField(max_length=255)),
                ('ingress', models.TextField()),
                ('text', models.TextField(blank=True)),
                ('event_type', models.PositiveSmallIntegerField(choices=[(0, 'Company presentation'), (1, 'Course'), (2, 'Party'), (3, 'Other'), (4, 'Event')], verbose_name='Event ype')),
                ('location', models.CharField(verbose_name='Location', max_length=100)),
                ('start_time', models.DateTimeField(verbose_name='Start time')),
                ('end_time', models.DateTimeField(verbose_name='End time')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('can_edit_groups', models.ManyToManyField(to='users.AbakusGroup', related_name='can_edit_event', null=True, blank=True)),
                ('can_edit_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='can_edit_event', null=True, blank=True)),
                ('can_view_groups', models.ManyToManyField(to='users.AbakusGroup', related_name='can_view_event', null=True, blank=True)),
                ('created_by', models.ForeignKey(default=None, null=True, related_name='event_created', editable=False, to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(default=None, null=True, related_name='event_updated', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['start_time'],
            },
            bases=(models.Model,),
        ),
    ]
