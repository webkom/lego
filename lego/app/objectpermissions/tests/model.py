# -*- coding: utf8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from basis.models import BasisModel

from lego.app.objectpermissions.models import ObjectPermissionsMixin


class TestModel(BasisModel, ObjectPermissionsMixin):
    name = models.CharField(_('name'), max_length=30)
