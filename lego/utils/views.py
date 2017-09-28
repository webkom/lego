from django.conf import settings
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from lego.apps.companies.models import Company
from lego.apps.email.models import EmailList
from lego.apps.gallery.models import Gallery
from lego.apps.joblistings.models import Joblisting
from lego.apps.meetings.models import Meeting
from lego.apps.notifications.models import Announcement
from lego.apps.permissions.constants import CREATE, LIST
from lego.apps.quotes.models import Quote
from lego.apps.users.models import AbakusGroup, User


class SiteMetaViewSet(viewsets.ViewSet):

    permission_classes = [permissions.AllowAny]

    def list(self, request):
        user = request.user
        site_meta = settings.SITE

        entities = {
            'companies': (Company, LIST),
            'joblistings': (Joblisting, LIST),
            'meetings': (Meeting, LIST),
            'quotes': (Quote, LIST),
            'galleries': (Gallery, LIST),

            # Admin:
            'announcements': (Announcement, CREATE),
            'groups': (AbakusGroup, CREATE),
            'email': (EmailList, CREATE),
            'users': (User, CREATE),
        }

        is_allowed = {}
        for entity, (model, permission) in entities.items():
            is_allowed[entity] = user.has_perm(permission, model)

        return Response({
            'site': site_meta,
            'is_allowed': is_allowed
        })
