# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20141113_2313'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='abakusgroup',
            options={'permissions': (('retrieve_abakusgroup', 'Can retrieve AbakusGroups'),)},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': (('retrieve_user', 'Can retrieve user'), ('list_user', 'Can list users'))},
        ),
        migrations.AlterField(
            model_name='abakusgroup',
            name='description',
            field=models.CharField(max_length=200, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='abakusgroup',
            name='name',
            field=models.CharField(unique=True, max_length=80),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='abakusgroup',
            name='parent',
            field=models.ForeignKey(to='users.AbakusGroup', related_name='children', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='abakusgroup',
            name='permission_groups',
            field=models.ManyToManyField(null=True, to='auth.Group', blank=True, related_name='abakus_groups'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='membership',
            name='abakus_group',
            field=models.ForeignKey(to='users.AbakusGroup'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='membership',
            name='end_date',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='membership',
            name='is_active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='membership',
            name='role',
            field=models.CharField(choices=[('M', 'Member'), ('L', 'Leader'), ('CL', 'Co-Leader'), ('T', 'Treasurer')], max_length=2, default='M'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='membership',
            name='start_date',
            field=models.DateField(auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='abakus_groups',
            field=models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', to='users.AbakusGroup', related_name='users', blank=True, through='users.Membership', related_query_name='user'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(help_text='Designates whether the user can log into this admin site.', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.  This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], max_length=30, error_messages={'unique': 'A user with that username already exists.'}),
            preserve_default=True,
        ),
    ]
