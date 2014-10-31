# -*- coding: utf8 -*-
from .models import UserMapping, GroupMapping, RawMapping


def get_recipients(local_part):
    recipients = []

    def query_recipients(queryset):
        mail_list = []
        for mapping in queryset:
            for address in mapping.get_recipients():
                mail_list.append(address)
        return mail_list

    recipients += query_recipients(UserMapping.objects.filter(address=local_part))
    recipients += query_recipients(GroupMapping.objects.filter(address=local_part))
    recipients += query_recipients(RawMapping.objects.filter(address=local_part))

    return set(recipients)
