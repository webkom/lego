from django.utils.functional import cached_property


class abakus_cached_property(cached_property):
    def __init__(self, func, name=None, delete_on_save=True):
        super().__init__(func, name)
        self.delete_on_save = delete_on_save
