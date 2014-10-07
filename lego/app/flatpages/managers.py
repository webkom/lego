# -*- coding: utf8 -*-
from basis.managers import BasisModelManager


class PublicPageManager(BasisModelManager):
    def get_queryset(self):
        return super(PublicPageManager, self).get_queryset().filter(require_auth=False,
                                                                    require_abakom=False)


class InternalPageManager(BasisModelManager):
    def get_queryset(self):
        return super(InternalPageManager, self).get_queryset().filter(require_abakom=False)
