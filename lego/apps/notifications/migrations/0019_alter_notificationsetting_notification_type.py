# Generated by Django 4.2.16 on 2025-04-20 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0018_alter_notificationsetting_notification_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notificationsetting",
            name="notification_type",
            field=models.CharField(
                choices=[
                    ("lending_request", "lending_request"),
                    ("lending_request_status_update", "lending_request_status_update"),
                    ("announcement", "announcement"),
                    ("restricted_mail_sent", "restricted_mail_sent"),
                    ("weekly_mail", "weekly_mail"),
                    ("event_bump", "event_bump"),
                    ("event_admin_registration", "event_admin_registration"),
                    ("event_admin_unregistration", "event_admin_unregistration"),
                    ("event_payment_overdue", "event_payment_overdue"),
                    ("meeting_invite", "meeting_invite"),
                    ("meeting_invitation_reminder", "meeting_invitation_reminder"),
                    ("penalty_creation", "penalty_creation"),
                    ("comment_reply", "comment_reply"),
                    ("registration_reminder", "registration_reminder"),
                    ("survey_created", "survey_created"),
                    ("event_payment_overdue_creator", "event_payment_overdue_creator"),
                    ("company_interest_created", "company_interest_created"),
                    ("inactive_warning", "inactive_warning"),
                    ("deleted_warning", "deleted_warning"),
                ],
                max_length=64,
            ),
        ),
    ]
