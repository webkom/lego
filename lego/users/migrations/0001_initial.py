# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status', default=False)),
                ('username', models.CharField(validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.  This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], error_messages={'unique': 'A user with that username already exists.'}, unique=True, max_length=30, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', verbose_name='username')),
                ('first_name', models.CharField(max_length=30, blank=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, blank=True, verbose_name='last name')),
                ('email', models.EmailField(max_length=75, blank=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.', verbose_name='staff status', default=False)),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active', default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AbakusGroup',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=80, unique=True, verbose_name='name')),
                ('is_committee', models.BooleanField(verbose_name='is committee', default=False)),
                ('leader', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name='leader', on_delete=django.db.models.deletion.SET_NULL)),
                ('parent', models.ForeignKey(to='users.AbakusGroup', blank=True, null=True, verbose_name='parent')),
                ('permissions', models.ManyToManyField(blank=True, to='auth.Permission', verbose_name='permissions')),
            ],
            options={
                'verbose_name_plural': 'groups',
                'verbose_name': 'group',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)),
                ('updated_at', models.DateTimeField(auto_now=True, default=datetime.datetime.now)),
                ('start_date', models.DateField(verbose_name='start date')),
                ('end_date', models.DateField(blank=True, verbose_name='end date')),
                ('permission_status', models.PositiveSmallIntegerField(default=2, choices=[(0, 'Previous member'), (1, "Previous member who's still active"), (2, 'Active member'), (3, 'Leader')], verbose_name='permission status')),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='membership_created', default=None, editable=False, null=True)),
                ('group', models.ForeignKey(to='users.AbakusGroup', verbose_name='group')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)),
                ('updated_at', models.DateTimeField(auto_now=True, default=datetime.datetime.now)),
                ('name', models.CharField(max_length=30, verbose_name='name')),
                ('description', models.CharField(max_length=150, verbose_name='description')),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='role_created', default=None, editable=False, null=True)),
                ('updated_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='role_updated', default=None, editable=False, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='membership',
            name='role',
            field=models.ForeignKey(to='users.Role', verbose_name='role'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='membership',
            name='updated_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='membership_updated', default=None, editable=False, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='user'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(through='users.Membership', to='users.AbakusGroup', related_name='user_set', related_query_name='user', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(to='auth.Permission', related_name='user_set', related_query_name='user', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
            preserve_default=True,
        ),
    ]
