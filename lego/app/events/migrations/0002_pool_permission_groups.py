# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150826_2000'),
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pool',
            name='permission_groups',
            field=models.ManyToManyField(to='users.AbakusGroup'),
        ),
    ]
