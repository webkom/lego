# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import basis.models
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(max_length=30, error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.  This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], unique=True)),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False, help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(verbose_name='active', default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('name', models.CharField(max_length=80, verbose_name='name', unique=True)),
                ('description', models.CharField(max_length=200, verbose_name='description', blank=True)),
                ('parent', models.ForeignKey(blank=True, null=True, verbose_name='parent', to='users.AbakusGroup')),
                ('permission_groups', models.ManyToManyField(verbose_name='permission groups', related_name='abakus_groups', blank=True, to='auth.Group')),
            ],
            options={
                'verbose_name': 'abakus group',
                'verbose_name_plural': 'abakus groups',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('created_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('updated_at', models.DateTimeField(editable=False, default=basis.models._now)),
                ('deleted', models.BooleanField(editable=False, default=False)),
                ('role', models.CharField(max_length=2, verbose_name='role', choices=[('M', 'Member'), ('L', 'Leader'), ('CL', 'Co-Leader'), ('T', 'Treasurer')], default='M')),
                ('is_active', models.BooleanField(verbose_name='is active', default=True)),
                ('start_date', models.DateField(verbose_name='start date', auto_now_add=True)),
                ('end_date', models.DateField(verbose_name='end date', blank=True, null=True)),
                ('abakus_group', models.ForeignKey(verbose_name='abakus group', to='users.AbakusGroup')),
                ('created_by', models.ForeignKey(editable=False, related_name='membership_created', null=True, default=None, to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(editable=False, related_name='membership_updated', null=True, default=None, to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL)),
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
            field=models.ManyToManyField(related_name='users', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='abakus groups', related_query_name='user', through='users.Membership', to='users.AbakusGroup'),
            preserve_default=True,
        ),
    ]
