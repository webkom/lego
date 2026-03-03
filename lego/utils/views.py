from django.conf import settings
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from lego.apps.companies.models import Company
from lego.apps.email.models import EmailList
from lego.apps.featureflags.models import FeatureFlag
from lego.apps.meetings.models import Meeting
from lego.apps.notifications.models import Announcement
from lego.apps.permissions.constants import CREATE, LIST
from lego.apps.polls.models import Poll
from lego.apps.quotes.models import Quote
from lego.apps.surveys.models import Survey
from lego.apps.users.models import AbakusGroup, Penalty, User


class SiteMetaViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        user = request.user
        site_meta = settings.SITE

        # Allow non-logged in users to see these as well:
        allow_anonymous_entities = [
            "events",
            "articles",
            "joblistings",
            "galleries",
        ]

        # Whereas these require that a user has keyword permissions:
        permission_entities = {
            "companies": (Company, LIST),
            "meetings": (Meeting, LIST),
            "polls": (Poll, LIST),
            "quotes": (Quote, LIST),
            "interest_groups": (AbakusGroup, LIST),
            "surveys": (Survey, LIST),
            # Admin:
            "bdb": (Company, CREATE),
            "announcements": (Announcement, CREATE),
            "penalties": (Penalty, CREATE),
            "groups": (AbakusGroup, CREATE),
            "email": (EmailList, CREATE),
            "users": (User, CREATE),
        }

        is_allowed = {entity: True for entity in allow_anonymous_entities}
        for entity, (model, permission) in permission_entities.items():
            is_allowed[entity] = user.has_perm(permission, model)
        if user.is_authenticated and user.memberships:
            is_allowed["sudo"] = user.memberships.filter(
                abakus_group__name="Webkom",
                is_active=True,
            ).exists()
        else:
            is_allowed["sudo"] = False
        for flag in FeatureFlag.objects.filter(allowed_identifier__isnull=False):
            if user.is_authenticated and flag.can_see_flag(user):
                is_allowed[flag.allowed_identifier] = True
            else:
                is_allowed[flag.allowed_identifier] = False
        return Response({"site": site_meta, "is_allowed": is_allowed})
