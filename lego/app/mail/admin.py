# -*- coding: utf8 -*-
from django.contrib import admin

from .models import UserMapping, GroupMapping

admin.site.register(UserMapping)
admin.site.register(GroupMapping)
