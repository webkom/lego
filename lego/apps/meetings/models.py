from datetime import timedelta

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.db import models
from django.utils import timezone

from lego.apps.comments.models import Comment
from lego.apps.content.fields import ContentField
from lego.apps.meetings import constants
from lego.apps.meetings.permissions import (
    MeetingInvitationPermissionHandler,
    MeetingPermissionHandler,
)
from lego.apps.reactions.models import Reaction
from lego.apps.users.models import User
from lego.utils.models import BasisModel


class Meeting(BasisModel):
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, default="")
    comments = GenericRelation(Comment)
    mazemap_poi = models.PositiveIntegerField(null=True)
    reactions = GenericRelation(Reaction)
    report = ContentField(blank=True, allow_images=True)
    report_author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        related_name="meetings_reports",
        on_delete=models.SET_NULL,
    )
    _invited_users = models.ManyToManyField(
        User,
        through="MeetingInvitation",
        related_name="meeting_invitation",
        through_fields=("meeting", "user"),
    )
    is_recurring = models.BooleanField(default=False, null=False, blank=True)
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    is_template = models.BooleanField(default=False, null=False, blank=False)

    def get_next_occurrence(self):
        if not self.is_recurring:
            return None

        next_occurrence = self.start_time + timedelta(days=7)

        while next_occurrence < timezone.now():
            next_occurrence += timedelta(days=7)

        return next_occurrence

    def save(self, *args, **kwargs):
        previous_report = None
        if self.pk:
            old_meeting = Meeting.objects.filter(pk=self.pk).only("report").first()
            if old_meeting:
                previous_report = old_meeting.report

        super().save(*args, **kwargs)

        if previous_report != self.report:
            ReportChangelog.objects.create(
                meeting=self, report=self.report, current_user=self.updated_by
            )

    def get_reactions_grouped(self, user):
        grouped = {}
        for reaction in self.reactions.all():
            if reaction.emoji.pk not in grouped:
                grouped[reaction.emoji.pk] = {
                    "emoji": reaction.emoji.pk,
                    "unicode_string": reaction.emoji.unicode_string,
                    "count": 0,
                    "has_reacted": False,
                    "reaction_id": None,
                }

            grouped[reaction.emoji.pk]["count"] += 1

            if reaction.created_by == user:
                grouped[reaction.emoji.pk]["has_reacted"] = True
                grouped[reaction.emoji.pk]["reaction_id"] = reaction.id

        return sorted(grouped.values(), key=lambda kv: kv["count"], reverse=True)

    class Meta:
        permission_handler = MeetingPermissionHandler()
        indexes = [
            models.Index(fields=["is_recurring", "is_template", "parent"]),
            models.Index(
                fields=[
                    "created_by",
                    "is_recurring",
                    "is_template",
                    "parent",
                    "start_time",
                ]
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(parent__isnull=False, is_template=True),
                name="prevent_template_with_parent",
            ),
            models.CheckConstraint(
                check=models.Q(is_recurring=False) | models.Q(is_template=True),
                name="recurring_meetings_must_be_templates",
            ),
        ]

    @property
    def invited_users(self):
        """
        As _invited_users include invitations deleted by Meeting.uninvite,
        we need to use this property method to not show them.
        For some reason, limit_choices_to does not work with ManyToManyField
        when specifying a custom through table.
        """
        return self._invited_users.filter(invitations__deleted=False)

    def get_absolute_url(self):
        return f"{settings.FRONTEND_URL}/meetings/{self.id}/"

    @property
    def participants(self):
        return self.invited_users.filter(invitations__status=constants.ATTENDING)

    def invite_user(self, user, created_by=None):
        invitation, created = self.invitations.update_or_create(
            user=user, meeting=self, defaults={"created_by": created_by}
        )

        return invitation, created

    def invite_group(self, group, created_by=None):
        for user in group.users.all():
            self.invite_user(user, created_by)

    def uninvite_user(self, user):
        invitation = self.invitations.get(user=user)
        invitation.delete(force=True)

    def restricted_lookup(self):
        """
        Restricted mail
        """
        return self.invited_users, []

    def announcement_lookup(self, meeting_invitation_status) -> list[User]:
        meeting_invitations = self.invitations

        if meeting_invitation_status:
            meeting_invitations = meeting_invitations.filter(
                status=meeting_invitation_status
            )

        return User.objects.filter(
            id__in=meeting_invitations.values_list("user", flat=True)
        )

    @property
    def content_target(self):
        return f"{self._meta.app_label}.{self._meta.model_name}-{self.pk}"


class MeetingInvitation(BasisModel):
    meeting = models.ForeignKey(
        Meeting, related_name="invitations", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, related_name="invitations", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=50,
        choices=constants.INVITATION_STATUS_TYPES,
        default=constants.NO_ANSWER,
    )

    class Meta:
        unique_together = ("meeting", "user")
        permission_handler = MeetingInvitationPermissionHandler()

    def generate_invitation_token(self):
        data = signing.dumps({"user_id": self.user.id, "meeting_id": self.meeting.id})

        token = TimestampSigner().sign(data)
        return token

    @staticmethod
    def validate_token(token):
        """
        Validate token.

        returns MeetingInvitation or None
        """

        try:
            # Valid in 7 days
            valid_in = 60 * 60 * 24 * 7
            data = signing.loads(TimestampSigner().unsign(token, max_age=valid_in))

            return MeetingInvitation.objects.filter(
                user=int(data["user_id"]), meeting=int(data["meeting_id"])
            )[0]
        except (BadSignature, SignatureExpired):
            return None

    def accept(self):
        self.status = constants.ATTENDING
        self.save()

    def reject(self):
        self.status = constants.NOT_ATTENDING
        self.save()


class ReportChangelog(BasisModel):
    meeting = models.ForeignKey(
        Meeting, related_name="report_changelogs", on_delete=models.CASCADE
    )
    report = ContentField(blank=True, allow_images=True)

    class Meta:
        ordering = ["-created_at"]
