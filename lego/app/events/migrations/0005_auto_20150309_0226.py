# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import basis.models
from django.conf import settings
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0004_auto_20150218_2135'),
    ]

    operations = [
        migrations.CreateModel(
            name='WaitingList',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('created_by', models.ForeignKey(editable=False, default=None, related_name='waitinglist_created', null=True, to=settings.AUTH_USER_MODEL)),
                ('event', models.OneToOneField(to='events.Event', related_name='waiting_list')),
                ('updated_by', models.ForeignKey(editable=False, default=None, related_name='waitinglist_updated', null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='registration',
            name='registration_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 9, 2, 26, 41, 681963, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='waiting_list',
            field=models.ForeignKey(to='events.WaitingList', null=True, related_name='registrations'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='waiting_pool',
            field=models.ForeignKey(to='events.Pool', null=True, related_name='waiting_registration'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='pool',
            field=models.ForeignKey(to='events.Pool', null=True, related_name='registrations'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='registrations'),
            preserve_default=True,
        ),
    ]
