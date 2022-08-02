from __future__ import absolute_import

from django.conf.urls import url

from oauth2_provider import views

from lego.utils.types import URLList

from .views import LegoAuthorizationView

urlpatterns: URLList = [
    url(r"^authorize/$", LegoAuthorizationView.as_view(), name="authorize"),
    url(r"^token/$", views.TokenView.as_view(), name="token"),
    url(r"^revoke_token/$", views.RevokeTokenView.as_view(), name="revoke-token"),
]
