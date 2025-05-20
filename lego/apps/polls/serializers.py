from typing import Iterator

from django.db import transaction
from rest_framework import serializers
from rest_framework.fields import CharField, IntegerField

from lego.apps.comments.serializers.comments import CommentSerializer
from lego.apps.polls.models import Option, Poll
from lego.apps.tags.serializers import TagSerializerMixin
from lego.utils.serializers import BasisModelSerializer


class OptionSerializer(BasisModelSerializer):
    class Meta:
        model = Option
        fields = ("id", "name", "votes")


class HiddenResultsOptionSerializer(BasisModelSerializer):
    class Meta:
        model = Option
        fields = ("id", "name")


class OptionUpdateSerializer(OptionSerializer):
    id = IntegerField(read_only=False)


class PollSerializer(BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    content_target = CharField(read_only=True)

    options = HiddenResultsOptionSerializer(many=True)
    total_votes = IntegerField(read_only=True)

    has_answered = serializers.SerializerMethodField()

    def get_has_answered(self, obj):
        user = self.context["request"].user
        return obj.get_has_answered(user)

    class Meta:
        model = Poll
        fields = (
            "id",
            "created_at",
            "valid_until",
            "title",
            "description",
            "options",
            "results_hidden",
            "total_votes",
            "tags",
            "comments",
            "content_target",
            "has_answered",
            "pinned",
        )


class DetailedPollSerializer(TagSerializerMixin, BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    content_target = CharField(read_only=True)

    options = OptionSerializer(many=True)
    total_votes = IntegerField(read_only=True)

    has_answered = serializers.SerializerMethodField()

    def get_has_answered(self, obj):
        user = self.context["request"].user
        return obj.get_has_answered(user)

    class Meta:
        model = Poll
        fields = (
            "id",
            "created_at",
            "valid_until",
            "title",
            "description",
            "options",
            "results_hidden",
            "total_votes",
            "comments",
            "content_target",
            "tags",
            "has_answered",
            "pinned",
        )


class HiddenResultsDetailedPollSerializer(DetailedPollSerializer):
    options = HiddenResultsOptionSerializer(many=True)  # type: ignore


class PollCreateSerializer(TagSerializerMixin, BasisModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Poll
        fields = (
            "id",
            "created_at",
            "title",
            "description",
            "options",
            "results_hidden",
            "total_votes",
            "tags",
            "pinned",
            "valid_until",
        )

    @transaction.atomic
    def create(self, validated_data):
        options_data = validated_data.pop("options")
        poll = super().create(validated_data)
        for option in options_data:
            Option.objects.create(poll=poll, **option)
        return poll


class PollUpdateSerializer(TagSerializerMixin, BasisModelSerializer):
    options = OptionUpdateSerializer(many=True)

    class Meta:
        model = Poll
        fields = (
            "id",
            "created_at",
            "title",
            "description",
            "options",
            "results_hidden",
            "total_votes",
            "tags",
            "pinned",
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        options = validated_data.pop("options")

        # Update the regular fields that aren't options first
        super().update(instance, validated_data)

        # Delete options that aren't in the received list
        existing_options_ids: Iterator[int] = (
            option["id"] for option in options if "id" in option
        )
        for old_option in instance.options.all():
            if old_option.id not in existing_options_ids:
                old_option.delete()

        # Add or update option, depending on the received option has an id
        for option in options:
            if "id" in option:
                Option.objects.filter(id=option["id"]).update(**option)
            else:
                Option.objects.create(poll=instance, **option)
        return instance
