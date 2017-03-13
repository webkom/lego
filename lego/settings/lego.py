from datetime import timedelta

SITE = {
    'name': 'Lego',
    'slogan': 'LEGO Er Ganske Oppdelt',
    'contact_email': 'webkom@abakus.no',
    'documentation_url': 'http://lego.readthedocs.io/'
}

API_VERSION = 'v1'
LOGIN_REDIRECT_URL = f'/api/{API_VERSION}/'


ADMINS = (
    ('Webkom', 'djangoerrors@abakus.no'),
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

]
