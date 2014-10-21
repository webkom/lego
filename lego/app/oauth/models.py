# -*- coding: utf8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from oauth2_provider.models import AbstractApplication


class APIApplication(AbstractApplication):
    description = models.CharField(_('application description'), max_length=100, blank=True)
