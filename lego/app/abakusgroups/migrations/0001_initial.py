# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import basis.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbakusGroup',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('name', models.CharField(max_length=80, unique=True, verbose_name='name')),
                ('description', models.CharField(max_length=200, unique=True, verbose_name='description')),
                ('created_by', models.ForeignKey(related_name='abakusgroup_created', to=settings.AUTH_USER_MODEL, default=None, editable=False, null=True)),
                ('parent', models.ForeignKey(blank=True, verbose_name='parent', to='abakusgroups.AbakusGroup', null=True)),
                ('permission_groups', models.ManyToManyField(blank=True, related_query_name='abakusgroups', related_name='abakusgroups', to='auth.Group', verbose_name='permission groups')),
                ('updated_by', models.ForeignKey(related_name='abakusgroup_updated', to=settings.AUTH_USER_MODEL, default=None, editable=False, null=True)),
            ],
            options={
                'verbose_name_plural': 'abakus groups',
                'verbose_name': 'abakus group',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('role', models.CharField(max_length=2, choices=[('M', 'Member'), ('L', 'Leader'), ('CL', 'Co-Leader'), ('T', 'Treasurer')], default='M', verbose_name='role')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('start_date', models.DateField(verbose_name='start date', auto_now_add=True)),
                ('end_date', models.DateField(blank=True, verbose_name='end date', null=True)),
                ('abakusgroup', models.ForeignKey(to='abakusgroups.AbakusGroup', verbose_name='abakus group')),
                ('created_by', models.ForeignKey(related_name='membership_created', to=settings.AUTH_USER_MODEL, default=None, editable=False, null=True)),
                ('updated_by', models.ForeignKey(related_name='membership_updated', to=settings.AUTH_USER_MODEL, default=None, editable=False, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([('user', 'abakusgroup')]),
        ),
    ]
