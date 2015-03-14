# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_auto_20150311_0306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='event',
            field=models.ForeignKey(related_name='registrations', to='events.Event'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='user',
            field=models.ForeignKey(related_name='registrations', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
