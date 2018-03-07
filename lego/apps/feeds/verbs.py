"""
# Verb example
# Verbs need to have a unique id. This is just a example of how to create a new verb.

class CommentVerb(Verb):
    id = 1
    infinitive = 'payment'
    aggregation_group = '{verb}-{object_content_type}-{object_id}'

register(CommentVerb)
"""


class Verb:
    id = 0
    infinitive = ''

    def __str__(self):
        return self.infinitive


verbs = {}


def register(verb):
    global verbs
    verbs[verb.id] = verb


class EventRegisterVerb(Verb):
    id = 1
    infinitive = 'event_register'


register(EventRegisterVerb)


class EventCreateVerb(Verb):
    id = 2
    infinitive = 'event_create'


register(EventCreateVerb)


class RegistrationBumpVerb(Verb):
    id = 3
    infinitive = 'registration_bump'


register(RegistrationBumpVerb)


class PenaltyVerb(Verb):
    id = 4
    infinitive = 'penalty'


register(PenaltyVerb)


class AdminRegistrationVerb(Verb):
    id = 5
    infinitive = 'admin_registration'


register(AdminRegistrationVerb)


class PaymentOverdueVerb(Verb):
    id = 6
    infinitive = 'payment_overdue'


register(PaymentOverdueVerb)


class MeetingInvitationVerb(Verb):
    id = 7
    infinitive = 'meeting_invitation'
    aggregation_group = '{verb}-{actor_id}-{actor_content_type}-{date}'


register(MeetingInvitationVerb)


class RestrictedMailSent(Verb):
    id = 8
    infinitive = 'restricted_mail_sent'
    aggregation_group = '{verb}-{object_content_type}-{object_id}'


register(RestrictedMailSent)


class AnnouncementVerb(Verb):
    id = 9
    infinitive = 'announcement'
    aggregation_group = '{verb}-{object_content_type}-{object_id}'


register(AnnouncementVerb)


class CompanyInterestVerb(Verb):
    id = 10
    infinitive = 'company_interest'


register(CompanyInterestVerb)


class CommentVerb(Verb):
    id = 11
    infinitive = 'comment'


register(CommentVerb)


class CommentReplyVerb(Verb):
    id = 12
    infinitive = 'comment_reply'


register(CommentReplyVerb)


class GroupJoinVerb(Verb):
    id = 13
    infinitive = 'group_join'
    aggregation_group = '{verb}-{object_content_type}-{object_id}'


register(GroupJoinVerb)


class AdminUnregistrationVerb(Verb):
    id = 14
    infinitive = 'admin_unregistration'


register(AdminUnregistrationVerb)
