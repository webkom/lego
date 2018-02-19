from django.utils import timezone


class Activity:

    object_id = None
    object_content_type = None

    actor_id = None
    actor_content_type = None

    target_id = None
    target_content_type = None

    def __init__(self, actor, verb, object, target=None, time=None, extra_context=None):
        self.verb = verb
        self.time = time or timezone.now()

        self._set_instance_fields('actor', actor)
        self._set_instance_fields('object', object)
        self._set_instance_fields('target', target)

        self.extra_context = extra_context or {}

    @property
    def serialization_id(self):
        """
        serialization_id is used to keep items locally sorted and unique

        eg:
        activity.serialization_id = 1373266755000000000042008
        1373266755000 activity creation time as epoch with millisecond resolution
        0000000000042 activity left padded object_id (10 digits)
        008 left padded activity verb id (3 digits)
        """

        if not self.object_id:
            raise TypeError('Cant serialize activities without a object')
        if self.object_id >= 10**10 or self.verb.id >= 10**3:
            raise TypeError('Fatal: object_id / verb have too many digits!')
        if not self.time:
            raise TypeError('Cant serialize activities without a time')
        milliseconds = str(int(self.time.timestamp() * 1000))
        serialization_id_str = '%s%0.10d%0.3d' % (milliseconds, self.object_id, self.verb.id)
        serialization_id = int(serialization_id_str)
        return serialization_id

    def _set_instance_fields(self, field, instance):
        """
        Helper method used to store {field}_id and {field}_content_type fields.
        """
        id_field = '%s_id' % field
        content_type_field = '%s_content_type' % field

        if isinstance(instance, str):
            content_type, instanceid = instance.split('-')
            setattr(self, id_field, int(instanceid))
            setattr(self, content_type_field, content_type)
        elif instance is None:
            setattr(self, id_field, None)
            setattr(self, content_type_field, None)
        else:
            setattr(self, id_field, int(instance.id))
            setattr(
                self, content_type_field, f'{instance._meta.app_label}.{instance._meta.model_name}'
            )

    @property
    def actor(self):
        if self.actor_content_type and self.actor_id:
            return f'{self.actor_content_type}-{self.actor_id}'

    @property
    def object(self):
        if self.object_content_type and self.object_id:
            return f'{self.object_content_type}-{self.object_id}'

    @property
    def target(self):
        if self.target_content_type and self.target_id:
            return f'{self.target_content_type}-{self.target_id}'

    def __eq__(self, other):
        if not isinstance(other, Activity):
            raise ValueError(
                'Can only compare to Activity not %r of type %s' % (other, type(other))
            )
        return self.serialization_id == other.serialization_id

    def __lt__(self, other):
        return self.serialization_id < other.serialization_id

    def __hash__(self):
        return hash(self.serialization_id)
