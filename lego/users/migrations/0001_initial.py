# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone
import basis.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.  This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], verbose_name='username', max_length=30, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', error_messages={'unique': 'A user with that username already exists.'})),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=75, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('name', models.CharField(unique=True, max_length=80, verbose_name='name')),
                ('description', models.CharField(blank=True, max_length=200, verbose_name='description')),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, null=True, default=None, related_name='abakusgroup_created')),
                ('parent', models.ForeignKey(to='users.AbakusGroup', verbose_name='parent', null=True, blank=True)),
                ('permission_groups', models.ManyToManyField(related_query_name='abakus_groups', to='auth.Group', blank=True, related_name='abakus_groups', verbose_name='permission groups')),
                ('updated_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, null=True, default=None, related_name='abakusgroup_updated')),
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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('role', models.CharField(max_length=2, default='M', choices=[('M', 'Member'), ('L', 'Leader'), ('CL', 'Co-Leader'), ('T', 'Treasurer')], verbose_name='role')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('start_date', models.DateField(auto_now_add=True, verbose_name='start date')),
                ('end_date', models.DateField(null=True, blank=True, verbose_name='end date')),
                ('abakus_group', models.ForeignKey(to='users.AbakusGroup', verbose_name='abakus group')),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, null=True, default=None, related_name='membership_created')),
                ('updated_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, null=True, default=None, related_name='membership_updated')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([('user', 'abakus_group')]),
        ),
        migrations.AddField(
            model_name='user',
            name='abakus_groups',
            field=models.ManyToManyField(to='users.AbakusGroup', verbose_name='abakus groups', related_query_name='user', related_name='users', through='users.Membership', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', blank=True),
            preserve_default=True,
        ),
    ]
