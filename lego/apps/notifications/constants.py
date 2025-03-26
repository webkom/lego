EMAIL = "email"
PUSH = "push"

CHANNELS = [EMAIL, PUSH]

CHANNEL_CHOICES = [(channel, channel) for channel in CHANNELS]

# Generics
WEEKLY_MAIL = "weekly_mail"

# Event
EVENT_BUMP = "event_bump"
EVENT_ADMIN_REGISTRATION = "event_admin_registration"
EVENT_ADMIN_UNREGISTRATION = "event_admin_unregistration"
EVENT_PAYMENT_OVERDUE = "event_payment_overdue"
EVENT_PAYMENT_OVERDUE_CREATOR = "event_payment_overdue_creator"

# Meeting
MEETING_INVITE = "meeting_invite"
MEETING_INVITATION_REMINDER = "meeting_invitation_reminder"

# Penalty
PENALTY_CREATION = "penalty_creation"

# Inactive user
INACTIVE_WARNING = "inactive_warning"

# Delete user
DELETED_WARNING = "deleted_warning"

# Restricted Mail
RESTRICTED_MAIL_SENT = "restricted_mail_sent"

# Company
COMPANY_INTEREST_CREATED = "company_interest_created"

# Survey
SURVEY_CREATED = "survey_created"

# Comment
COMMENT_REPLY = "comment_reply"

# Notifications
ANNOUNCEMENT = "announcement"

# Followers
REGISTRATION_REMINDER = "registration_reminder"

NOTIFICATION_TYPES = [
    ANNOUNCEMENT,
    RESTRICTED_MAIL_SENT,
    WEEKLY_MAIL,
    EVENT_BUMP,
    EVENT_ADMIN_REGISTRATION,
    EVENT_ADMIN_UNREGISTRATION,
    EVENT_PAYMENT_OVERDUE,
    MEETING_INVITE,
    MEETING_INVITATION_REMINDER,
    PENALTY_CREATION,
    COMMENT_REPLY,
    REGISTRATION_REMINDER,
    SURVEY_CREATED,
    EVENT_PAYMENT_OVERDUE_CREATOR,
    COMPANY_INTEREST_CREATED,
    INACTIVE_WARNING,
    DELETED_WARNING,
]

NOTIFICATION_CHOICES = [
    (notification, notification) for notification in NOTIFICATION_TYPES
]
