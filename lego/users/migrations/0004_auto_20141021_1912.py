# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import basis.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_abakusgroup_leader'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='created_at',
            field=models.DateTimeField(editable=False, default=basis.models._now),
        ),
        migrations.AlterField(
            model_name='membership',
            name='updated_at',
            field=models.DateTimeField(editable=False, default=basis.models._now),
        ),
    ]
