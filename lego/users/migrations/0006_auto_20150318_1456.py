# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import basis.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='abakusgroup',
            name='created_at',
            field=models.DateTimeField(editable=False, default=basis.models._now),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='abakusgroup',
            name='updated_at',
            field=models.DateTimeField(editable=False, default=basis.models._now),
            preserve_default=True,
        ),
    ]
