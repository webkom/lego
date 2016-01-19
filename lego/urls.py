from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import TemplateView
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

urlpatterns = [
    url(r'^api/', include('lego.api.urls')),

    url(r'^authorization/token-auth/$', obtain_jwt_token,
        name='obtain_jwt_token'),
    url(r'^authorization/token-auth/refresh/$', refresh_jwt_token,
        name='refresh_jwt_token'),
    url(r'^authorization/oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^authorization/', include('rest_framework.urls', namespace='rest_framework')),
]

if not settings.DEBUG:
    urlpatterns += [
        url(r'^$', TemplateView.as_view(template_name='before_launch.html'), name='landing_page'),
    ]
else:  # pragma: no cover
    urlpatterns += [
        url(r'^$', TemplateView.as_view(template_name='base.html'), name='landing_page'),
    ]
