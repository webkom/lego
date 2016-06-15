from django.conf.urls import include, url
from django.contrib.auth.views import login, logout
from django.views.generic import TemplateView
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

urlpatterns = [
    url(r'^api/', include('lego.api.urls', namespace='api')),

    url(r'^authorization/token-auth/$', obtain_jwt_token, name='obtain_jwt_token'),
    url(r'^authorization/token-auth/refresh/$', refresh_jwt_token, name='refresh_jwt_token'),

    url(r'^authorization/oauth2/', include('lego.app.oauth.urls', namespace='oauth2_provider')),
    url(r'^authorization/login/', login, {'template_name': 'authorization/login.html'},
        name='login'),
    url(r'^authorization/logout/', logout, {'next_page': '/'}, name='logout'),

    url(r'^$', TemplateView.as_view(template_name='landing.html'), name='landing_page'),
]
