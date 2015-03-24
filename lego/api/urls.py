# -*- coding: utf8 -*-
from django.conf import settings
from django.conf.urls import include, patterns, url
from django.core.urlresolvers import resolve
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from .v1 import router as v1


@csrf_exempt
def version_redirect(request, path):
    new_path = '/api/{0}/{1}/'.format(settings.API_VERSION, path)

    match = resolve(new_path)

    if match.func == version_redirect:
        raise Http404

    return HttpResponseRedirect(new_path)

urlpatterns = patterns(
    '',
    url(r'^v1/', include(v1.urls)),
    url(r'token-auth/$', 'rest_framework_jwt.views.obtain_jwt_token', name='obtain_jwt_token'),
    url(r'token-auth/refresh/$', 'rest_framework_jwt.views.refresh_jwt_token',
        name='refresh_jwt_token'),
    url(r'^(.*)/$', version_redirect),
)
