SITE = {
    'name': 'Lego',
    'slogan': 'LEGO Er Ganske Oppdelt',
    'contact_email': 'webkom@abakus.no',
    'documentation_url': 'http://lego.readthedocs.io/'
}

API_VERSION = 'v1'
LOGIN_REDIRECT_URL = '/api/{0}/'.format(API_VERSION)


ADMINS = (
    ('Webkom', 'djangoerrors@abakus.no'),
)

MANAGERS = ADMINS
