# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_auto_20150309_0226'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='possible_pools',
            field=models.ForeignKey(related_name='possible_registrations', to='events.Pool', null=True),
            preserve_default=True,
        ),
    ]
