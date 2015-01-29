from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns(
    '',

    url(r'^api/', include('lego.api.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),

    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
)

if not settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^$', TemplateView.as_view(template_name='before_launch.html'), name='landing_page'),
    )
else:  # pragma: no cover
    urlpatterns += patterns(
        '',
        url(r'^$', TemplateView.as_view(template_name='base.html'), name='landing_page'),
    )
