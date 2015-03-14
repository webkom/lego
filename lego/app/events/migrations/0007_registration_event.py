# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_registration_possible_pools'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='event',
            field=models.ForeignKey(related_name='registrations', null=True, to='events.Event'),
            preserve_default=True,
        ),
    ]
