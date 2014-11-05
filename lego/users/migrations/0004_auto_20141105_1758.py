# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20141103_1725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='start_date',
            field=models.DateField(auto_now_add=True, verbose_name='start date'),
            preserve_default=True,
        ),
    ]
