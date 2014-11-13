# -*- coding: utf8 -*-
from basis.managers import PersistentModelManager


class PublicPageManager(PersistentModelManager):
    def get_queryset(self):
        return super(PublicPageManager, self).get_queryset().filter(require_auth=False,
                                                                    require_abakom=False)


class InternalPageManager(PersistentModelManager):
    def get_queryset(self):
        return super(InternalPageManager, self).get_queryset().filter(require_abakom=False)
