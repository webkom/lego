from django.conf import settings
from django.conf.urls import include, url
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.views.generic import TemplateView
from rest_framework.documentation import include_docs_urls

from rest_framework_jwt.views import (
    obtain_jwt_token,
    refresh_jwt_token,
    verify_jwt_token,
)

from lego.api.urls import urlpatterns as api

jwt_urlpatterns = [
    url(r"^token-auth/$", obtain_jwt_token, name="obtain_jwt_token"),
    url(r"^token-auth/refresh/$", refresh_jwt_token, name="refresh_jwt_token"),
    url(r"^token-auth/verify/$", verify_jwt_token, name="verify_jwt_token"),
]

authorization_urlpatterns = [
    url(r"^oauth2/", include("lego.apps.oauth.urls")),
    url(r"", include((jwt_urlpatterns, "jwt"), namespace="jwt")),
    url(
        r"^login/",
        LoginView.as_view(template_name="authorization/login.html"),
        name="login",
    ),
    url(r"^logout/", LogoutView.as_view(next_page="/"), name="logout"),
]

urlpatterns = [
    url(r"^api/", include("lego.api.urls", namespace="api")),
    url(r"^authorization/", include(authorization_urlpatterns)),  # type: ignore
    url(r"^health/", include("health_check.urls")),
    url(
        r"^api-docs/",
        include_docs_urls(
            title=settings.SITE["name"],
            description=settings.SITE["slogan"],
            patterns=api,  # type: ignore
            schema_url="/api",
        ),
    ),
    url(r"^$", TemplateView.as_view(template_name="landing.html"), name="landing_page"),
]

if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns  # type: ignore
