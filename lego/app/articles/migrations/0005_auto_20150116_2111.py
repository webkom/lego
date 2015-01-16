# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0004_auto_20150107_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='article',
            name='ingress',
            field=models.TextField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='article',
            name='text',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
    ]
