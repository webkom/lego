EMAIL = 'email'
PUSH = 'push'

CHANNELS = [EMAIL, PUSH]

CHANNEL_CHOICES = [(channel, channel) for channel in CHANNELS]


# Generics
WEEKLY_MAIL = 'weekly_mail'

# Event
EVENT_BUMP = 'event_bump'
EVENT_ADMIN_REGISTRATION = 'event_admin_registration'
EVENT_PAYMENT_OVERDUE = 'event_payment_overdue'

# Meeting
MEETING_INVITE = 'meeting_invite'

# Penalty
PENALTY_CREATION = 'penalty_creation'

# Restricted Mail
RESTRICTED_MAIL_SENT = 'restricted_mail_sent'

# Company
COMPANY_INTEREST_CREATED = 'company_interest_created'

# Comment
COMMENT = 'comment'
COMMENT_REPLY = 'comment_reply'

# Notifications
ANNOUNCEMENT = 'announcement'

NOTIFICATION_TYPES = [
    WEEKLY_MAIL,
    EVENT_BUMP,
    EVENT_ADMIN_REGISTRATION,
    EVENT_PAYMENT_OVERDUE,
    MEETING_INVITE,
    PENALTY_CREATION,
    RESTRICTED_MAIL_SENT,
    COMPANY_INTEREST_CREATED,
    COMMENT,
    COMMENT_REPLY,
    ANNOUNCEMENT
]

NOTIFICATION_CHOICES = [(notification, notification) for notification in NOTIFICATION_TYPES]
