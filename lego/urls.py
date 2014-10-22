from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib import auth

admin.autodiscover()

urlpatterns = patterns(
    '',

    url(r'^api/', include('lego.api.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', auth.views.login, {'template_name': 'login.html'}),


    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
)

if not settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^$', TemplateView.as_view(template_name="before_launch.html"), name='landing_page'),
    )
else:
    urlpatterns += patterns(
        '',
        url(r'^$', TemplateView.as_view(template_name="base.html"), name='landing_page'),
    )
