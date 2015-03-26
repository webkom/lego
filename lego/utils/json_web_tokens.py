# -*- coding: utf8 -*-
from lego.users.serializers import DetailedUserSerializer


def response_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': DetailedUserSerializer(user).data
    }
