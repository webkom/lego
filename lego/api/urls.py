# -*- coding: utf8 -*-
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from .v1 import router as v1


@csrf_exempt
def version_redirect(request, url_ending):
    return HttpResponseRedirect('/api/{0}/{1}'.format(settings.API_VERSION, url_ending))

urlpatterns = patterns(
    '',
    url(r'^v1/', include(v1.urls)),
    url(r'^(.*)', version_redirect),
)
