from __future__ import absolute_import

from django.urls import re_path

from oauth2_provider import views

from .views import LegoAuthorizationView

urlpatterns = (
    re_path(r"^authorize/$", LegoAuthorizationView.as_view(), name="authorize"),
    re_path(r"^token/$", views.TokenView.as_view(), name="token"),
    re_path(r"^revoke_token/$", views.RevokeTokenView.as_view(), name="revoke-token"),
)
