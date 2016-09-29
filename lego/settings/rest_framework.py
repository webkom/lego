REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'lego.utils.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'lego.apps.permissions.permissions.AbakusPermission',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'lego.apps.permissions.filters.AbakusObjectPermissionFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'lego.utils.pagination.APIPagination',
    'PAGE_SIZE': 30,
    'EXCEPTION_HANDLER': 'lego.utils.exceptions.exception_handler',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}
