from django.conf import settings
from ipware.ip import get_ip
from rest_framework import permissions


class HealthPermission(permissions.BasePermission):
    """
    Health checks is only allowed by approved ips. We restrict this because the health may be hard
    to calculate.

    Allowed ips is defined by the HEALTH_CHECK_REMOTE_IPS setting located in settings/lego.py
    """

    def has_permission(self, request, view):
        remote_ip = get_ip(request)
        if remote_ip:
            allowed_ips = [ip.lower() for ip in settings.HEALTH_CHECK_REMOTE_IPS]
            for allowed_ip in allowed_ips:
                if remote_ip.startswith(allowed_ip):
                    return True

        return False
