# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import basis.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('require_auth', models.BooleanField(verbose_name='require auth', default=False)),
                ('name', models.CharField(verbose_name='name', max_length=30)),
                ('can_edit_groups', models.ManyToManyField(blank=True, to='users.AbakusGroup', related_name='can_edit_testmodel', null=True)),
                ('can_edit_users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, related_name='can_edit_testmodel', null=True)),
                ('can_view_groups', models.ManyToManyField(blank=True, to='users.AbakusGroup', related_name='can_view_testmodel', null=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, related_name='testmodel_created', default=None, null=True)),
                ('updated_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, related_name='testmodel_updated', default=None, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
