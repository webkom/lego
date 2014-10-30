# -*- coding: utf8 -*-
from lego.users.views.user import UserViewSet
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
