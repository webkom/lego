from rest_framework.serializers import DateTimeField


class FeedDateTimeField(DateTimeField):
    """
    The internals of stream_framework does not operate with timezone aware datetimes. We have to
    make the datetimes timezone aware to make the frontend work as it is supposed to.
    """

    def to_representation(self, value):
        if not value:
            return None

        value = self.enforce_timezone(value)

        return super().to_representation(value)
