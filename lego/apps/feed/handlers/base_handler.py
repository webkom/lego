from lego.apps.feed.activities import FeedActivity
from lego.apps.feed.verbs import CreateVerb, DeleteVerb, UpdateVerb


class BaseHandler:
    verbs = dict(
        create=CreateVerb,
        update=UpdateVerb,
        delete=DeleteVerb
    )

    @classmethod
    def get_user_ids(cls, action):
        return []

    @classmethod
    def get_verb(cls, action):
        if action not in cls.verbs:
            raise Exception('Action not valid. Possibilites are: {}'.format(cls.verbs.keys()))
        return cls.verbs[action]

    @classmethod
    def get_actor(cls, instance, action):
        actor = instance
        if action == 'update' and hasattr(instance, 'updated_by'):
            actor = instance.updated_by
        elif hasattr(instance, 'created_by'):
            actor = instance.created_by
        return actor

    @classmethod
    def get_target(cls, instance, action):
        return instance

    @classmethod
    def get_object(cls, instance, action):
        return instance

    @classmethod
    def get_activity(cls, instance, action='create'):
        return FeedActivity(
            actor=cls.get_actor(instance, action),
            verb=cls.get_verb(action),
            object=cls.get_object(instance, action),
            target=cls.get_target(instance, action)
        )
