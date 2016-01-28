# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_auto_20160126_0816'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='unregistration_date',
            field=models.DateTimeField(null=True),
        ),
    ]
