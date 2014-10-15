# -*- coding: utf8 -*-
from rest_framework import routers

from lego.app.flatpages.api import PageViewSet


router = routers.DefaultRouter()
router.register(r'pages', PageViewSet)
