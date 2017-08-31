REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'lego.apps.oauth.authentication.Authentication',
        'rest_framework.authentication.SessionAuthentication',
        'lego.apps.jwt.authentication.Authentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'lego.utils.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'lego.apps.permissions.api.permissions.LegoPermissions',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'lego.apps.permissions.api.filters.LegoPermissionFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'lego.utils.pagination.CursorPagination',
    'PAGE_SIZE': 30,
    'EXCEPTION_HANDLER': 'lego.utils.exceptions.exception_handler',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}
