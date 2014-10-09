# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import django.db.models.deletion
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False,
                                        primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now,
                                                    verbose_name='last login')),
                ('is_superuser', models.BooleanField(
                    verbose_name='superuser status',
                    help_text='Designates that this user has all permissions without '
                              'explicitly assigning them.',
                    default=False
                )),
                ('username', models.CharField(
                    unique=True,
                    validators=[django.core.validators.RegexValidator(
                        '^[\\w.@+-]+$',
                        'Enter a valid username.  This value may contain only letters, '
                        'numbers and @/./+/-/_ characters.',
                        'invalid'
                    )],
                    help_text='Required. 30 characters or fewer. Letters, digits and'
                              '@/./+/-/_ only.',
                    max_length=30,
                    error_messages={'unique': 'A user with that username already exists.'},
                    verbose_name='username'
                )),
                ('first_name', models.CharField(max_length=30, verbose_name='first name',
                                                blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name',
                                               blank=True)),
                ('email',
                 models.EmailField(max_length=75, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(
                    verbose_name='staff status',
                    help_text='Designates whether the user can log into this admin site.',
                    default=False
                )),
                ('is_active', models.BooleanField(
                    verbose_name='active',
                    help_text='Designates whether this user should be treated as active. '
                              'Unselect this instead of deleting accounts.',
                    default=True
                )),
                ('date_joined', models.DateTimeField(
                    default=django.utils.timezone.now,
                    verbose_name='date joined'
                )),
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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False,
                                        primary_key=True)),
                ('name', models.CharField(max_length=80, unique=True, verbose_name='name')),
                ('leader',
                 models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                   blank=True, to=settings.AUTH_USER_MODEL, verbose_name='leader')),
                ('parent', models.ForeignKey(null=True, blank=True, to='users.AbakusGroup',
                                             verbose_name='parent')),
                ('permissions',
                 models.ManyToManyField(to='auth.Permission', verbose_name='permissions',
                                        blank=True)),
            ],
            options={
                'verbose_name_plural': 'groups',
                'verbose_name': 'group',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(
                related_name='user_set',
                help_text='The groups this user belongs to. A user will get all permissions '
                          'granted to each of their groups.',
                blank=True,
                to='users.AbakusGroup',
                related_query_name='user',
                verbose_name='groups'
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(
                related_name='user_set',
                help_text='Specific permissions for this user.',
                blank=True, to='auth.Permission',
                related_query_name='user',
                verbose_name='user permissions'
            ),
            preserve_default=True,
        ),
    ]
