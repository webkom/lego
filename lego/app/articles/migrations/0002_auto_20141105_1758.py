# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='can_edit',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='editable_articles'),
            preserve_default=True,
        ),
    ]
