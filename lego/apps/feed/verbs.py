"""
# Verb example
# Verbs need to have a unique id. This is just a example of how to create a new verb.
# Stream-Framework has the following verbs built-in: Follow, Comment, Love, Add

from stream_framework.verbs.base import Verb, register


class PaymentVerb(Verb):
    id = 5
    infinitive = 'payment'
    past_tense = infinitive

    aggregation_group = '{verb}-{object_content_type}-{object_id}'

register(PaymentVerb)
"""
from stream_framework.verbs.base import Comment as CommentVerb  # noqa
from stream_framework.verbs.base import Verb, register


class CreateVerb(Verb):
    id = 6
    infinitive = 'create'
    past_tense = 'created'


register(CreateVerb)


class UpdateVerb(Verb):
    id = 7
    infinitive = 'update'
    past_tense = 'updated'


register(UpdateVerb)


class DeleteVerb(Verb):
    id = 8
    infinitive = 'delete'
    past_tense = 'deleted'


register(DeleteVerb)
