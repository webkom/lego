from django.db import transaction
from rest_framework.fields import CharField, IntegerField
from lego.apps.comments.serializers import CommentSerializer
from lego.apps.polls.models import Poll, Option
from lego.apps.tags.serializers import TagSerializerMixin
from lego.utils.serializers import BasisModelSerializer
from rest_framework import serializers


class OptionSerializer(BasisModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'name', 'votes')


class OptionUpdateSerializer(OptionSerializer):

    id = IntegerField(read_only=False)


class PollSerializer(BasisModelSerializer):

    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)

    options = OptionSerializer(many=True)
    total_votes = IntegerField(read_only=True)

    has_answered = serializers.SerializerMethodField()

    def get_has_answered(self, obj):
        user = self.context['request'].user
        return user in obj.answered_users.all()

    class Meta:
        model = Poll
        fields = ('id', 'created_at', 'title', 'description', 'options',
                  'total_votes', 'tags', 'comments', 'comment_target',
                  'has_answered', 'pinned')


class DetailedPollSerializer(TagSerializerMixin, BasisModelSerializer):

    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)

    options = OptionSerializer(many=True)
    total_votes = IntegerField(read_only=True)

    has_answered = serializers.SerializerMethodField()

    def get_has_answered(self, obj):
        user = self.context['request'].user
        return user in obj.answered_users.all()

    class Meta:
        model = Poll
        fields = ('id', 'created_at', 'title', 'description', 'options',
                  'total_votes', 'comments', 'comment_target', 'tags',
                  'has_answered', 'pinned')


class PollCreateSerializer(TagSerializerMixin, BasisModelSerializer):

    options = OptionSerializer(many=True)

    class Meta:
        model = Poll
        fields = ('id', 'created_at', 'title', 'description', 'options',
                  'total_votes', 'tags', 'pinned')

    @transaction.atomic
    def create(self, validated_data):
        options_data = validated_data.pop('options')
        poll = super().create(validated_data)
        for option in options_data:
            Option.objects.create(poll=poll, **option)
        return poll


class PollUpdateSerializer(TagSerializerMixin, BasisModelSerializer):

    options = OptionUpdateSerializer(many=True)

    class Meta:
        model = Poll
        fields = ('id', 'created_at', 'title', 'description', 'options',
                  'total_votes', 'tags', 'pinned')

    @transaction.atomic
    def update(self, instance, validated_data):
        options = validated_data.pop('options')

        # Update the regular fields that aren't options first
        super().update(instance, validated_data)

        # Delete options that aren't in the received list
        for old_option in instance.options.all():
            options_with_ids = filter(lambda q: 'id' in q, options)
            existing_options_ids = map(lambda q: q['id'], options_with_ids)
            if old_option.id not in existing_options_ids:
                old_option.delete()

        # Add or update option, depending on the received option has an id
        for option in options:
            if 'id' in option:
                Option.objects.filter(id=option['id']).update(**option)
                Option.objects.get(id=option['id'])
            else:
                Option.objects.create(poll=instance, **option)\

        return instance
