from rest_framework import serializers


class AbakusGroupField(serializers.PrimaryKeyRelatedField):

    def __init__(self, **kwargs):
        if 'read_only' not in kwargs.keys() and 'queryset' not in kwargs.keys():
            kwargs['read_only'] = True
        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        return {'id': value.id, 'name': value.name}


class AbakusGroupListField(serializers.ManyRelatedField):

    def __init__(self, field_kwargs=None, **kwargs):
        if field_kwargs is None:
            field_kwargs = {}

        kwargs['child_relation'] = AbakusGroupField(**field_kwargs)
        super().__init__(**kwargs)


class PublicUserField(serializers.PrimaryKeyRelatedField):

    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        from lego.apps.users.serializers.users import PublicUserSerializer
        serializer = PublicUserSerializer(instance=value)
        return serializer.data


class PublicUserListField(serializers.ManyRelatedField):
    def __init__(self, field_kwargs=None, **kwargs):
        if field_kwargs is None:
            field_kwargs = {}

        kwargs['child_relation'] = PublicUserField(**field_kwargs)
        super().__init__(**kwargs)
