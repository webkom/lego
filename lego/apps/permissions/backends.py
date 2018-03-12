from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.db import models

from lego.apps.permissions.keyword import KeywordPermissions
from lego.apps.permissions.utils import get_permission_handler
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import AuthFailed


class LegoPermissionBackend(ModelBackend):
    """
    Check permissions on a object using the builtin django user.has_perms() function.
    """

    def authenticate(self, request, username=None, password="", **kwargs):
        return super().authenticate(request, username, password, **kwargs)

    def _get_permissions(self, user_obj, obj, from_name):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        return set()

    def has_module_perms(self, user_obj, app_label):
        return False

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_anonymous and not user_obj.is_active:
            return False

        if obj is None:
            # Take a shortcut and check KeywordPermissions only if no object are defined.
            return KeywordPermissions.has_perm(user_obj, perm)

        if isinstance(obj, models.Model):
            permission_handler = get_permission_handler(obj)
            return permission_handler.has_perm(user_obj, perm, obj=obj)
        elif isinstance(obj, models.QuerySet):
            permission_handler = get_permission_handler(obj.model)
            return permission_handler.has_perm(user_obj, perm, queryset=obj)
        elif issubclass(obj, models.Model):
            permission_handler = get_permission_handler(obj)
            return permission_handler.has_perm(
                user_obj, perm, queryset=obj.objects.none()
            )

        return False


class FeideBackend(BaseOAuth2):
    """Feide OAuth authentication backend"""

    name = "feide"
    AUTHORIZATION_URL = "https://auth.dataporten.no/oauth/authorization"
    ACCESS_TOKEN_URL = "https://auth.dataporten.no/oauth/token"
    ACCESS_TOKEN_METHOD = "POST"
    SCOPE_SEPARATOR = " "
    REDIRECT_STATE = False
    ID_KEY = "userid"
    USER_FIELDS = ["username", "email", "first_name", "last_name"]
    EXTRA_DATA = [
        ("email", "email"),
        ("groups", "groups"),
        ("expires_id", "expires_in"),
        ("scope", "scope"),
    ]

    def get_user_details(self, response):
        """Return user details from Github account"""
        fullname, first_name, last_name = self.get_user_names(response.get("name"))

        email = response.get("email", "")
        username = email.split("@")[0]

        return {
            "username": username,
            "email": email,
            "fullname": fullname,
            "first_name": first_name,
            "last_name": last_name,
        }

    def user_data(self, access_token, *args, **kwargs):
        user_info = self._user_info(access_token)
        groups = self._user_groups(access_token)

        if user_info["audience"] != settings.SOCIAL_AUTH_FEIDE_KEY:
            raise AuthFailed(self, "The audience returned by feide is not valid.")

        return {**user_info["user"], "groups": groups}

    def _user_info(self, access_token):
        url = "https://auth.dataporten.no/userinfo"
        return self.get_json(url, headers={"Authorization": f"Bearer {access_token}"})

    def _user_groups(self, access_token):
        url = "https://groups-api.dataporten.no/groups/me/groups"
        return self.get_json(url, headers={"Authorization": f"Bearer {access_token}"})
