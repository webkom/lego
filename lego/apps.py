# -*- coding: utf8 -*-

from django.apps import AppConfig

from lego.utils.signals import load_initial_data


class LegoConfig(AppConfig):
    name = 'lego'

    def ready(self):
        load_initial_data.attach_signals()
