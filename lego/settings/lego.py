# -*- coding: utf8 -*-
import sys

API_VERSION = 'v1'
LOGIN_REDIRECT_URL = '/api/{0}/'.format(API_VERSION)
TESTING = 'test' in sys.argv  # Check if manage.py test has been run
