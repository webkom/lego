from rest_framework import serializers
from rest_framework.fields import CharField

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.content.fields import ContentSerializerField
from lego.apps.meetings import constants
from lego.apps.meetings.models import (
    Meeting,
    MeetingInvitation,
    MeetingTemplate,
    ReportChangelog,
)
from lego.apps.reactions.models import Reaction
from lego.apps.users.fields import AbakusGroupField, PublicUserField
from lego.apps.users.models import AbakusGroup, User
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.fields import PrimaryKeyRelatedFieldNoPKOpt
from lego.utils.serializers import BasisModelSerializer


class BasicMeetingSerializer(BasisModelSerializer):

    class Meta:
        fields = (
            "id",
            "title",
            "report",
            "location",
            "start_time",
            "end_time",
            "description",
            "mazemap_poi",
            "report_author",
            "created_by",
        )


class MeetingInvitationSerializer(BasisModelSerializer):
    user = PublicUserSerializer()
    status = serializers.ChoiceField(
        choices=(constants.ATTENDING, constants.NOT_ATTENDING)
    )

    class Meta:
        model = MeetingInvitation
        fields = ("user", "status", "meeting")

    def create(self, validated_data):
        meeting = Meeting.objects.get(id=self.context["view"].kwargs["meeting_pk"])
        meeting_invitation = MeetingInvitation.objects.create(
            meeting=meeting, **validated_data
        )
        return meeting_invitation


class MeetingInvitationUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = MeetingInvitation
        fields = ("status",)


class ReactionsSerializer(serializers.ModelSerializer):
    author = PublicUserSerializer(read_only=True, source="created_by")

    class Meta:
        model = Reaction
        fields = ("id", "emoji", "author")
        read_only = True


class MeetingGroupInvite(serializers.Serializer):
    group = PrimaryKeyRelatedFieldNoPKOpt(queryset=AbakusGroup.objects.all())


class MeetingUserInvite(serializers.Serializer):
    user = PrimaryKeyRelatedFieldNoPKOpt(queryset=User.objects.all())


class MeetingBulkInvite(serializers.Serializer):
    users = PrimaryKeyRelatedFieldNoPKOpt(
        queryset=User.objects.all(), many=True, required=False
    )
    groups = PrimaryKeyRelatedFieldNoPKOpt(
        queryset=AbakusGroup.objects.all(), many=True, required=False
    )


class ReportChangelogSerializer(BasisModelSerializer):
    created_by = PublicUserField(read_only=True)

    class Meta:
        model = ReportChangelog
        fields = ["report", "created_at", "created_by"]


class MeetingDetailSerializer(BasisModelSerializer):
    invitations = MeetingInvitationSerializer(many=True, read_only=True)
    report = ContentSerializerField()
    report_changelogs = ReportChangelogSerializer(many=True, read_only=True)
    report_author = PublicUserField(
        queryset=User.objects.all(), allow_null=True, required=False
    )
    created_by = PublicUserField(read_only=True)
    comments = CommentSerializer(read_only=True, many=True)
    content_target = CharField(read_only=True)
    reactions_grouped = serializers.SerializerMethodField()
    reactions = ReactionsSerializer(many=True, read_only=True)

    def get_reactions_grouped(self, obj):
        user = self.context["request"].user
        return obj.get_reactions_grouped(user)

    class Meta:
        model = Meeting
        fields = BasicMeetingSerializer.Meta.fields + (
            "report_changelogs",
            "invitations",
            "comments",
            "content_target",
            "reactions_grouped",
            "reactions",
        )
        read_only = True

    def create(self, validated_data):
        meeting = Meeting.objects.create(**validated_data)
        owner = validated_data["current_user"]
        meeting.invite_user(owner, owner)
        return meeting


class MeetingListSerializer(BasisModelSerializer):
    report_author = PublicUserField(
        queryset=User.objects.all(), allow_null=True, required=False
    )
    created_by = PublicUserField(read_only=True)

    class Meta:
        model = Meeting
        fields = (
            "id",
            "created_by",
            "title",
            "location",
            "start_time",
            "end_time",
            "report_author",
            "mazemap_poi",
        )


class MeetingSearchSerializer(serializers.ModelSerializer):
    report = ContentSerializerField()

    class Meta:
        model = Meeting
        fields = (
            "id",
            "title",
            "description",
            "report",
            "start_time",
        )
        read_only = True


class MeetingTemplateSerializer(BasisModelSerializer):
    report = ContentSerializerField()
    report_author = PublicUserField(
        queryset=User.objects.all(), allow_null=True, required=False
    )
    invited_users = PublicUserField(
        queryset=User.objects.all(), allow_null=True, required=False, many=True
    )
    invited_groups = AbakusGroupField(
        queryset=AbakusGroup.objects.all(), allow_null=True, required=False, many=True
    )
    location = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = MeetingTemplate
        fields = BasicMeetingSerializer.Meta.fields + (
            "invited_users",
            "invited_groups",
        )
