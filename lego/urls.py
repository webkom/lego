from django.conf.urls import include, url
from django.contrib.auth.views import login, logout
from django.views.generic import TemplateView
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

jwt_urlpatterns = [
    url(r'^token-auth/$', obtain_jwt_token, name='obtain_jwt_token'),
    url(r'^token-auth/refresh/$', refresh_jwt_token, name='refresh_jwt_token'),
    url(r'^token-auth/verify/$', verify_jwt_token, name='verify_jwt_token'),
]

authorization_urlpatterns = [
    url(r'^oauth2/', include('lego.apps.oauth.urls', namespace='oauth2_provider')),
    url(r'', include(jwt_urlpatterns, namespace='jwt')),
    url(r'^login/', login, {'template_name': 'authorization/login.html'}, name='login'),
    url(r'^logout/', logout, {'next_page': '/'}, name='logout'),
]

urlpatterns = [
    url(r'^api/', include('lego.api.urls', namespace='api')),
    url(r'^authorization/', include(authorization_urlpatterns)),
    url(r'^$', TemplateView.as_view(template_name='landing.html'), name='landing_page'),
]
