from datetime import timedelta

SITE = {
    'name': 'LEGO',
    'slogan': 'LEGO Er Ganske Oppdelt',
    'contact_email': 'webkom@abakus.no',
    'documentation_url': '/docs/',
    'domain': 'abakus.no',
    'owner': 'Abakus Linjeforening'
}

API_VERSION = 'v1'
LOGIN_REDIRECT_URL = f'/api/{API_VERSION}/'

EMAIL_SUBJECT_PREFIX = u'[{}] '.format(SITE['name'])

ADMINS = (
    ('Webkom', 'webkom@abakus.no'),
)

MANAGERS = ADMINS

SEARCH_INDEX = 'lego-search'

PENALTY_DURATION = timedelta(days=20)
# Tuples for ignored (month, day) intervals
PENALTY_IGNORE_SUMMER = (
    (6, 1), (8, 15)
)
PENALTY_IGNORE_WINTER = (
    (12, 1), (1, 10)
)

HEALTH_CHECK_REMOTE_IPS = [
    '10.',
    '127.0.0.'
]

# Additional groups to sync with LDAP. Committees is synced automatically. Add group names.
LDAP_GROUPS = [
    'Webkom',
    'Fagkom'
]

LMTP_HOST = '0.0.0.0'
LMTP_PORT = 8024

RESTRICTED_ADDRESS = 'restricted'
RESTRICTED_DOMAIN = 'abakus.no'
RESTRICTED_FROM = 'Abakus Linjeforening <no-reply@abakus.no>'
RESTRICTED_ALLOW_ORIGINAL_SENDER = False

GSUITE_DOMAIN = 'abakus.no'
