# -*- coding: utf8 -*-
from django.conf.urls import patterns, url, include

from .v1 import router as v1


urlpatterns = patterns(
    '',
    url(r'', include(v1.urls)),
    url(r'^v1/', include(v1.urls)),
)
