from django.conf import settings
from django.conf.urls import include
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, re_path
from django.views.generic import TemplateView
from rest_framework.documentation import include_docs_urls

from rest_framework_jwt.views import (
    ObtainJSONWebTokenView,
    refresh_jwt_token,
    verify_jwt_token,
)

from lego.api.urls import urlpatterns as api
from lego.apps.users.models import User
from lego.utils.types import URLList


# START
# Temporary view to generate crypt_hashes for the users that do not have it
class TokenAuthView(ObtainJSONWebTokenView):
    def post(self, request, *args, **kwargs):
        result = super().post(request, *args, **kwargs)
        # If the login is invalid it would have raised an exception by this point
        user = User.objects.get(username=request.data.get("username"))
        if user.crypt_password_hash == "":
            user.set_password(request.data.get("password"))
            user.save()
        return result


obtain_jwt_token = TokenAuthView.as_view()
# END

jwt_urlpatterns: URLList = [
    re_path(r"^token-auth/$", obtain_jwt_token, name="obtain_jwt_token"),
    re_path(r"^token-auth/refresh/$", refresh_jwt_token, name="refresh_jwt_token"),
    re_path(r"^token-auth/verify/$", verify_jwt_token, name="verify_jwt_token"),
]

authorization_urlpatterns: URLList = [
    re_path(r"^oauth2/", include("lego.apps.oauth.urls")),
    re_path(r"", include((jwt_urlpatterns, "jwt"), namespace="jwt")),
    re_path(
        r"^login/",
        LoginView.as_view(template_name="authorization/login.html"),
        name="login",
    ),
    re_path(r"^logout/", LogoutView.as_view(next_page="/"), name="logout"),
]

urlpatterns: URLList = [
    re_path(r"^api/", include("lego.api.urls", namespace="api")),
    re_path(r"^authorization/", include(authorization_urlpatterns)),  # type: ignore
    re_path(r"^health/", include("health_check.urls")),
    re_path(
        r"^api-docs/",
        include_docs_urls(
            title=settings.SITE["name"],
            description=settings.SITE["slogan"],
            patterns=api,  # type: ignore
            schema_url="/api",
        ),
    ),
    re_path(
        r"^$", TemplateView.as_view(template_name="landing.html"), name="landing_page"
    ),
]

if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls)), *urlpatterns]
