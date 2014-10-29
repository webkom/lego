# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import django.utils.timezone
from django.conf import settings
import basis.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.  This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], max_length=30, verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=75, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AbakusGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(unique=True, max_length=80, verbose_name='name')),
                ('parent', models.ForeignKey(to='users.AbakusGroup', null=True, blank=True, verbose_name='parent')),
                ('permissions', models.ManyToManyField(to='auth.Permission', blank=True, verbose_name='permissions')),
            ],
            options={
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('title', models.CharField(default='Member', blank=True, max_length=30, verbose_name='role')),
                ('start_date', models.DateField(verbose_name='start date')),
                ('end_date', models.DateField(blank=True, verbose_name='end date')),
                ('permission_status', models.PositiveSmallIntegerField(default=2, choices=[(0, 'Previous member'), (1, "Previous member who's still active"), (2, 'Active member'), (3, 'Leader')], verbose_name='permission status')),
                ('created_by', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, null=True, related_name='membership_created', editable=False)),
                ('group', models.ForeignKey(to='users.AbakusGroup', verbose_name='group')),
                ('updated_by', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, null=True, related_name='membership_updated', editable=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_name='user_set', to='users.AbakusGroup', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', through='users.Membership', blank=True, related_query_name='user', verbose_name='groups'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(related_name='user_set', to='auth.Permission', help_text='Specific permissions for this user.', blank=True, related_query_name='user', verbose_name='user permissions'),
            preserve_default=True,
        ),
    ]
