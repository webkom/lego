# Generated by Django 4.0.10 on 2023-10-04 19:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0041_user_linkedin_id_alter_user_github_username'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LendableObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('title', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True)),
                ('has_contract', models.BooleanField(default=False)),
                ('max_lending_period', models.DurationField(null=True)),
                ('responsible_role', models.CharField(choices=[('member', 'member'), ('leader', 'leader'), ('co-leader', 'co-leader'), ('treasurer', 'treasurer'), ('recruiting', 'recruiting'), ('development', 'development'), ('editor', 'editor'), ('retiree', 'retiree'), ('media_relations', 'media_relations'), ('active_retiree', 'active_retiree'), ('alumni', 'alumni'), ('webmaster', 'webmaster'), ('interest_group_admin', 'interest_group_admin'), ('alumni_admin', 'alumni_admin'), ('retiree_email', 'retiree_email'), ('company_admin', 'company_admin'), ('dugnad_admin', 'dugnad_admin'), ('trip_admin', 'trip_admin'), ('sponsor_admin', 'sponsor_admin'), ('social_admin', 'social_admin')], default='member', max_length=30)),
                ('created_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('responsible_groups', models.ManyToManyField(to='users.abakusgroup')),
                ('updated_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'default_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='LendingInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('start_date', models.DateTimeField(null=True)),
                ('end_date', models.DateTimeField(null=True)),
                ('pending', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('lendable_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lending.lendableobject')),
                ('updated_by', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'default_manager_name': 'objects',
            },
        ),
    ]
