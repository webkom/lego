# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['start_time'], 'permissions': (('retrieve_event', 'Can retrieve event'), ('list_event', 'Can list event'))},
        ),
        migrations.AlterField(
            model_name='event',
            name='end_time',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='event_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Company presentation'), (1, 'Course'), (2, 'Party'), (3, 'Other'), (4, 'Event')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='location',
            field=models.CharField(max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='start_time',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
    ]
