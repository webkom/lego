from .lego import API_VERSION, SITE

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "lego.apps.oauth.authentication.Authentication",
        "lego.apps.jwt.authentication.Authentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": ["lego.utils.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": [
        "djangorestframework_camel_case.parser.CamelCaseJSONParser"
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "lego.apps.permissions.api.permissions.LegoPermissions"
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "lego.apps.permissions.api.filters.LegoPermissionFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "lego.utils.pagination.CursorPagination",
    "PAGE_SIZE": 30,
    "EXCEPTION_HANDLER": "lego.utils.exceptions.exception_handler",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "TEST_REQUEST_RENDERER_CLASSES": ["lego.utils.renderers.JSONRenderer"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": SITE["name"],
    "DESCRIPTION": SITE["slogan"],
    "VERSION": API_VERSION,
    "SCHEMA_PATH_PREFIX": f"/api/{API_VERSION}",
    "SERVE_INCLUDE_SCHEMA": False,
    # Serve the Swagger assets ourselves; the default is an unpinned jsdelivr bundle.
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    # The API camelizes both directions, so the schema has to describe camelCase.
    "CAMELIZE_NAMES": True,
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
    ],
}
