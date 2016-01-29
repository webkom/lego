SITE = {
    'name': 'Lego',
    'slogan': 'LEGO Er Ganske Oppdelt'
}

API_VERSION = 'v1'
LOGIN_REDIRECT_URL = '/api/{0}/'.format(API_VERSION)
PARENT_LOOKUP_PREFIX = 'parent_lookup_'

ADMINS = (
    ('Webkom', 'djangoerrors@abakus.no'),
)

MANAGERS = ADMINS
