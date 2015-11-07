# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20151106_1903'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registration',
            name='waiting_pool',
        ),
        migrations.AddField(
            model_name='registration',
            name='waiting_pool',
            field=models.ForeignKey(to='events.Pool', related_name='waiting_registrations', null=True),
        ),
    ]
