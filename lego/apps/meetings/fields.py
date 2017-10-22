from rest_framework import serializers


class MeetingField(serializers.PrimaryKeyRelatedField):

    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        return {'id': value.id, 'title': value.title}


class MeetingListField(serializers.ManyRelatedField):
    def __init__(self, field_kwargs=None, **kwargs):
        if field_kwargs is None:
            field_kwargs = {}

        kwargs['child_relation'] = MeetingField(**field_kwargs)
        super().__init__(**kwargs)
