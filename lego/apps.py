# -*- coding: utf8 -*-

from django.apps import AppConfig


class LegoConfig(AppConfig):
    name = 'lego'

    def ready(self):
        from lego.utils.signals import load_initial_data
