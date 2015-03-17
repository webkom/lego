# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20150116_2248'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='deleted',
            field=models.BooleanField(default=False, editable=False),
            preserve_default=True,
        ),
    ]
