# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import lego.app.mail.mixins
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0002_auto_20141031_1555'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenericMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('address', models.CharField(verbose_name='Addess', max_length=100, unique=True)),
                ('additional_users', models.ManyToManyField(blank=True, verbose_name='Additional Users', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(to='users.AbakusGroup', verbose_name='Group', related_name='mail_mappings')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, lego.app.mail.mixins.MappingResult),
        ),
        migrations.CreateModel(
            name='OneTimeMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('address', models.CharField(verbose_name='Addess', max_length=100, unique=True)),
                ('token', models.CharField(verbose_name='Token', max_length=36, default='1a68bad1-437e-4b5a-b225-8446b59623a0', unique=True)),
                ('from_address', models.EmailField(verbose_name='From Address', max_length=75)),
                ('timeout', models.DateTimeField(verbose_name='Timeout', default=datetime.datetime(2014, 10, 31, 17, 28, 37, 732110))),
                ('generic_mappings', models.ManyToManyField(to='mail.GenericMapping', verbose_name='Generic Mappings', related_name='one_time_mappings')),
                ('group_mappings', models.ManyToManyField(to='mail.GroupMapping', verbose_name='Groups', related_name='one_time_mappings')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, lego.app.mail.mixins.MappingResult),
        ),
        migrations.CreateModel(
            name='RawMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('email', models.EmailField(verbose_name='Raw email', max_length=75)),
                ('raw_mapping', models.ForeignKey(to='mail.RawMapping', verbose_name='Raw Mail Mapping', related_name='recipients')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('address', models.CharField(verbose_name='Addess', max_length=100, unique=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='User', related_name='mail_mappings')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, lego.app.mail.mixins.MappingResult),
        ),
    ]
