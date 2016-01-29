from django.conf.urls import include, url
from django.views.generic import TemplateView
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

urlpatterns = [
    url(r'^api/', include('lego.api.urls', namespace='api')),

    url(r'^authorization/token-auth/$', obtain_jwt_token, name='obtain_jwt_token'),
    url(r'^authorization/token-auth/refresh/$', refresh_jwt_token, name='refresh_jwt_token'),

    url(r'^authorization/oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^authorization/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^$', TemplateView.as_view(template_name='landing.html'), name='landing_page'),
]
