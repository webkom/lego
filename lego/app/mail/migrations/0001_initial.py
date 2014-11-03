# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lego.app.mail.mixins
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenericMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model, lego.app.mail.mixins.MappingResult),
        ),
        migrations.CreateModel(
            name='GroupMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(verbose_name='Addess', max_length=100, unique=True)),
                ('additional_users', models.ManyToManyField(verbose_name='Additional Users', blank=True, to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(verbose_name='Group', related_name='mail_mappings', to='users.AbakusGroup')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, lego.app.mail.mixins.MappingResult),
        ),
        migrations.CreateModel(
            name='OneTimeMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(verbose_name='Addess', max_length=100, unique=True)),
                ('token', models.CharField(verbose_name='Token', max_length=36, default='50fe7e48-999b-48b9-9faf-2401efc62be7', unique=True)),
                ('from_address', models.EmailField(verbose_name='From Address', max_length=75)),
                ('timeout', models.DateTimeField(verbose_name='Timeout', default=datetime.datetime(2014, 11, 3, 12, 5, 10, 210893))),
                ('generic_mappings', models.ManyToManyField(verbose_name='Generic Mappings', related_name='one_time_mappings', to='mail.GenericMapping')),
                ('group_mappings', models.ManyToManyField(verbose_name='Groups', related_name='one_time_mappings', to='mail.GroupMapping')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, lego.app.mail.mixins.MappingResult),
        ),
        migrations.CreateModel(
            name='RawMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(verbose_name='Addess', max_length=100, unique=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, lego.app.mail.mixins.MappingResult),
        ),
        migrations.CreateModel(
            name='RawMappingElement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(verbose_name='Raw email', max_length=75)),
                ('raw_mapping', models.ForeignKey(verbose_name='Raw Mail Mapping', related_name='recipients', to='mail.RawMapping')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(verbose_name='Addess', max_length=100, unique=True)),
                ('user', models.ForeignKey(verbose_name='User', related_name='mail_mappings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, lego.app.mail.mixins.MappingResult),
        ),
    ]
