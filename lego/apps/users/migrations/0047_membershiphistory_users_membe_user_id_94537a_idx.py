# Generated by Django 4.2.16 on 2025-03-18 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0046_alter_membership_unique_together_and_more"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="membershiphistory",
            index=models.Index(
                fields=["user", "abakus_group"], name="users_membe_user_id_94537a_idx"
            ),
        ),
    ]
