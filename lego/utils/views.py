from django.conf import settings
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from lego.apps.articles.models import Article
from lego.apps.companies.models import Company
from lego.apps.email.models import EmailList
from lego.apps.events.models import Event
from lego.apps.gallery.models import Gallery
from lego.apps.joblistings.models import Joblisting
from lego.apps.meetings.models import Meeting
from lego.apps.notifications.models import Announcement
from lego.apps.permissions.constants import LIST
from lego.apps.quotes.models import Quote
from lego.apps.social_groups.models import InterestGroup
from lego.apps.users.models import AbakusGroup


class SiteMetaViewSet(viewsets.ViewSet):

    permission_classes = [permissions.AllowAny]

    def list(self, request):
        user = request.user
        site_meta = settings.SITE

        entities = {
            'events': Event,
            'articles': Article,
            'companies': Company,
            'intrest_groups': InterestGroup,
            'joblistings': Joblisting,
            'announcements': Announcement,
            'meetings': Meeting,
            'quotes': Quote,
            'galleries': Gallery,
            'groups': AbakusGroup,
            'email': EmailList,
        }

        entity_permissions = [
            (entity, user.has_perm(LIST, model)) for entity, model in entities.items()
        ]

        menu_items = [entity for entity, has_perm in entity_permissions if has_perm]

        return Response({
            'site': site_meta,
            'menu_items': menu_items
        })
