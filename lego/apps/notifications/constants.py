EMAIL = 'email'

CHANNELS = [EMAIL]

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


NOTIFICATION_TYPES = [
    WEEKLY_MAIL,
    EVENT_BUMP,
    EVENT_ADMIN_REGISTRATION,
    EVENT_PAYMENT_OVERDUE,
    MEETING_INVITE,
    PENALTY_CREATION,
]

NOTIFICATION_CHOICES = [(notification, notification) for notification in NOTIFICATION_TYPES]
