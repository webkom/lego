from django.conf.urls import include, url
from django.views.generic import TemplateView
from oauth2_provider import views as oauth2_views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

oauth2_urlpatterns = [
    url(r'^authorize/$', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    url(r'^token/$', oauth2_views.TokenView.as_view(), name="token"),
    url(r'^revoke_token/$', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

jwt_urlpatterns = [
    url(r'^token-auth/$', obtain_jwt_token, name='obtain_jwt_token'),
    url(r'^token-auth/refresh/$', refresh_jwt_token, name='refresh_jwt_token'),
]

authorization_urlpatterns = [
    url(r'^oauth2/', include(oauth2_urlpatterns, namespace='oauth2_provider')),
    url(r'', include(jwt_urlpatterns, namespace='jwt')),
    url(r'', include('rest_framework.urls', namespace='rest_framework')),
]

urlpatterns = [
    url(r'^api/', include('lego.api.urls', namespace='api')),

    url(r'^authorization/', include(authorization_urlpatterns)),

    url(r'^$', TemplateView.as_view(template_name='landing.html'), name='landing_page'),
]
