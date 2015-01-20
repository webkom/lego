# -*- coding: utf8 -*-
from basis.managers import PersistentModelManager


class AbakusGroupManager(PersistentModelManager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
