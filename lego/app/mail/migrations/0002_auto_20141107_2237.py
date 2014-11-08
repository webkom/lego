# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rawmappingelement',
            name='raw_mapping',
        ),
        migrations.DeleteModel(
            name='RawMapping',
        ),
        migrations.DeleteModel(
            name='RawMappingElement',
        ),
        migrations.AlterField(
            model_name='onetimemapping',
            name='timeout',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 7, 22, 52, 46, 503912), verbose_name='Timeout'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='onetimemapping',
            name='token',
            field=models.CharField(unique=True, default='40311cf7-8da3-463c-a586-f3536d761fe6', verbose_name='Token', max_length=36),
            preserve_default=True,
        ),
    ]
