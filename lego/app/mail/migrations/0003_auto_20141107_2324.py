# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import basis.models


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0002_auto_20141107_2237'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='onetimemapping',
            name='address',
        ),
        migrations.AddField(
            model_name='groupmapping',
            name='created_at',
            field=models.DateTimeField(default=basis.models._now, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groupmapping',
            name='updated_at',
            field=models.DateTimeField(default=basis.models._now, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='onetimemapping',
            name='created_at',
            field=models.DateTimeField(default=basis.models._now, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='onetimemapping',
            name='updated_at',
            field=models.DateTimeField(default=basis.models._now, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='usermapping',
            name='created_at',
            field=models.DateTimeField(default=basis.models._now, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='usermapping',
            name='updated_at',
            field=models.DateTimeField(default=basis.models._now, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='onetimemapping',
            name='timeout',
            field=models.DateTimeField(verbose_name='Timeout', default=datetime.datetime(2014, 11, 7, 23, 39, 17, 261281)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='onetimemapping',
            name='token',
            field=models.CharField(unique=True, max_length=36, verbose_name='Token', default='564bf014-c6ed-48c5-8417-aa94516b66b2'),
            preserve_default=True,
        ),
    ]
