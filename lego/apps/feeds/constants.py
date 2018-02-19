COMMENT = 'comment'
COMMENT_REPLY = 'comment_reply'
EVENT_REGISTER = 'event_register'
EVENT_CREATE = 'event_create'
REGISTRATION_BUMP = 'registration_bump'
PENALTY = 'penalty'
ADMIN_REGISTRATION = 'admin_registration'
ADMIN_UNREGISTRATION = 'admin_unregistration'
PAYMENT_OVERDUE = 'payment_overdue'
MEETING_INVITATION = 'meeting_invitation'
RESTRICTED_MAIL_SENT = 'restricted_mail_sent'
ANNOUNCEMENT = 'announcement'
COMPANY_INTEREST = 'company_interest'
GROUP_JOIN = 'group_join'
"""
The VERBS dict defines allowed verbs or types of a feed element.
The aggregation group is used to group similar items into one feed element.
"""
VERBS = {
    COMMENT: {},
    COMMENT_REPLY: {},
    EVENT_REGISTER: {},
    EVENT_CREATE: {},
    REGISTRATION_BUMP: {},
    PENALTY: {},
    ADMIN_REGISTRATION: {},
    ADMIN_UNREGISTRATION: {},
    PAYMENT_OVERDUE: {},
    MEETING_INVITATION: {
        'aggregation_group': '{verb}-{actor_id}-{actor_content_type}-{date}'
    },
    RESTRICTED_MAIL_SENT: {
        'aggregation_group': '{verb}-{object_content_type}-{object_id}'
    },
    ANNOUNCEMENT: {
        'aggregation_group': '{verb}-{object_content_type}-{object_id}',
    },
    COMPANY_INTEREST: {},
    GROUP_JOIN: {
        'aggregation_group': '{verb}-{object_content_type}-{object_id}'
    }
}

VERB_CHOICES = ((VERB, VERB) for VERB in VERBS.keys())
