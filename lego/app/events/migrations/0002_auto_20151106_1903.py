# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registration',
            name='waiting_pool',
        ),
        migrations.AddField(
            model_name='registration',
            name='waiting_pool',
            field=models.ManyToManyField(null=True, related_name='waiting_registrations', to='events.Pool'),
        ),
    ]
