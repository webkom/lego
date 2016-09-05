from rest_framework.serializers import Field


class AbakusGroupListField(Field):
    """
    Render a list of AbakusGroup as a list of strings.
    """
    def to_representation(self, value):
        return [group.name for group in value]
