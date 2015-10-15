# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0003_auto_20151008_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quotelike',
            name='quote',
            field=models.ForeignKey(to='quotes.Quote'),
        ),
    ]
