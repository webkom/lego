from lego.apps.feed.activities import FeedActivity
from lego.apps.feed.verbs import CreateVerb, DeleteVerb, UpdateVerb


class BaseHandler:
    verbs = dict(
        create=CreateVerb,
        update=UpdateVerb,
        delete=DeleteVerb
    )

    def __init__(self, instance, action):
        self.instance = instance
        self.action = action

    @property
    def user_ids(self):
        return []

    @property
    def verb(self):
        if self.action not in self.verbs:
            raise Exception('Action not valid. Possibilites are: {}'.format(self.verbs.keys()))
        return self.verbs[self.action]

    @property
    def actor(self):
        actor = self.instance
        if self.action == 'update' and hasattr(self.instance, 'updated_by'):
            actor = self.instance.updated_by
        elif hasattr(self.instance, 'created_by'):
            actor = self.instance.created_by
        return actor

    @property
    def target(self):
        return self.instance

    @property
    def object(self):
        return self.instance

    @property
    def activity(self):
        return FeedActivity(
            actor=self.actor,
            verb=self.verb,
            object=self.object,
            target=self.target
        )
