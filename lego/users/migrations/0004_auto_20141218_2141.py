# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20141113_2313'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='abakusgroup',
            options={'verbose_name_plural': 'abakus groups', 'verbose_name': 'abakus group', 'permissions': (('retrieve_abakusgroup', 'Can retrieve AbakusGroups'), ('list_abakusgroup', 'Can list AbakusGroups'))},
        ),
    ]
