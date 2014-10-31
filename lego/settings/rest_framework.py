# -*- coding: utf8 -*-

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}
