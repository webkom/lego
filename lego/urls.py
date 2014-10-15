from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns(
    '',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('lego.api.urls')),
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
