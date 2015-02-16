# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import basis.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0002_auto_20150203_1946'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('name', models.CharField(max_length=100)),
                ('size', models.PositiveSmallIntegerField(default=0)),
                ('activation_date', models.DateTimeField()),
                ('created_by', models.ForeignKey(related_name='pool_created', editable=False, to=settings.AUTH_USER_MODEL, null=True, default=None)),
                ('event', models.ForeignKey(related_name='pools', to='events.Event')),
                ('updated_by', models.ForeignKey(related_name='pool_updated', editable=False, to=settings.AUTH_USER_MODEL, null=True, default=None)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('created_by', models.ForeignKey(related_name='registration_created', editable=False, to=settings.AUTH_USER_MODEL, null=True, default=None)),
                ('pool', models.ForeignKey(related_name='registrations', to='events.Pool')),
                ('updated_by', models.ForeignKey(related_name='registration_updated', editable=False, to=settings.AUTH_USER_MODEL, null=True, default=None)),
                ('user', models.OneToOneField(related_name='registrations', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='registration',
            unique_together=set([('user', 'pool')]),
        ),
        migrations.AddField(
            model_name='event',
            name='merge_date',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
