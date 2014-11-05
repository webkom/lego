# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20141105_1758'),
        ('articles', '0003_auto_20141105_1833'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='can_edit',
            new_name='users_can_edit',
        ),
        migrations.AddField(
            model_name='article',
            name='can_view',
            field=models.ManyToManyField(to='users.AbakusGroup', related_name='viewable_articles'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='groups_can_edit',
            field=models.ManyToManyField(to='users.AbakusGroup', related_name='editable_articles'),
            preserve_default=True,
        ),
    ]
