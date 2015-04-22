# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import basis.models
import django.contrib.postgres.fields
import django.core.validators
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, blank=True, verbose_name='last login')),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('username', models.CharField(unique=True, error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.  This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')])),
                ('first_name', models.CharField(max_length=30, blank=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, blank=True, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, blank=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AbakusGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('name', models.CharField(unique=True, max_length=80)),
                ('description', models.CharField(max_length=200, blank=True)),
                ('permissions', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30), null=True, size=None, verbose_name='permissions')),
                ('parent', models.ForeignKey(related_name='children', to='users.AbakusGroup', null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('updated_at', models.DateTimeField(default=basis.models._now, editable=False)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('role', models.CharField(max_length=2, default='M', choices=[('M', 'Member'), ('L', 'Leader'), ('CL', 'Co-Leader'), ('T', 'Treasurer')])),
                ('is_active', models.BooleanField(default=True)),
                ('start_date', models.DateField(auto_now_add=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('abakus_group', models.ForeignKey(to='users.AbakusGroup')),
                ('created_by', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, related_name='membership_created', null=True, editable=False)),
                ('updated_by', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, related_name='membership_updated', null=True, editable=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='abakus_groups',
            field=models.ManyToManyField(related_name='users', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', to='users.AbakusGroup', blank=True, related_query_name='user', through='users.Membership'),
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([('user', 'abakus_group')]),
        ),
        migrations.AlterUniqueTogether(
            name='abakusgroup',
            unique_together=set([('name',)]),
        ),
    ]
