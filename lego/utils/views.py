from django.conf import settings
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from lego.apps.articles.models import Article
from lego.apps.companies.models import Company
from lego.apps.events.models import Event
from lego.apps.gallery.models import Gallery
from lego.apps.joblistings.models import Joblisting
from lego.apps.meetings.models import Meeting
from lego.apps.notifications.models import Announcement
from lego.apps.permissions.constants import LIST
from lego.apps.quotes.models import Quote
from lego.apps.social_groups.models import InterestGroup


def check_permission(user, entity, model):
    return (entity, user.has_perm(LIST, model))


class SiteMetaViewSet(viewsets.ViewSet):

    permission_classes = [permissions.AllowAny]

    def list(self, request):
        user = request.user
        site_meta = settings.SITE

        entities = {
            'events': Event.objects.all(),
            'articles': Article.objects.all(),
            'companies': Company.objects.all(),
            'intrest_groups': InterestGroup.objects.all(),
            'joblistings': Joblisting.objects.all(),
            'announcements': Announcement.objects.all(),
            'meetings': Meeting.objects.all(),
            'quotes': Quote.objects.all(),
            'galleries': Gallery.objects.all()
        }

        entity_permissions = [
            check_permission(user, entity, model) for entity, model in entities.items()
        ]

        menu_items = [entity for entity, has_perm in entity_permissions if has_perm]

        return Response({
            'site': site_meta,
            'menu_items': menu_items
        })
