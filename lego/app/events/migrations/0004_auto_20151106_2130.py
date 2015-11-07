# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20151106_2048'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registration',
            name='waiting_pool',
        ),
        migrations.AddField(
            model_name='registration',
            name='waiting_pool',
            field=models.ManyToManyField(related_name='waiting_registrations', to='events.Pool', null=True),
        ),
    ]
