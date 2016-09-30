from rest_framework import routers

from lego.apps.articles.views import ArticlesViewSet
from lego.apps.bdb.views import CompanyContactViewSet, CompanyViewSet, SemesterStatusViewSet
from lego.apps.comments.views import CommentViewSet
from lego.apps.events.views import EventViewSet, PoolViewSet, RegistrationViewSet
from lego.apps.events.webhooks import StripeWebhook
from lego.apps.feed.views import NotificationFeedViewSet
from lego.apps.files.views import FileViewSet
from lego.apps.flatpages.views import PageViewSet
from lego.apps.meetings.views import MeetingInvitationViewSet, MeetingViewSet
from lego.apps.oauth.views import AccessTokenViewSet, ApplicationViewSet
from lego.apps.quotes.views import QuoteViewSet
from lego.apps.reactions.views import ReactionTypeViewSet, ReactionViewSet
from lego.apps.search.views import AutocompleteViewSet, SearchViewSet
from lego.apps.social_groups.views import InterestGroupViewSet
from lego.apps.users.views.abakus_groups import AbakusGroupViewSet
from lego.apps.users.views.memberships import MembershipViewSet
from lego.apps.users.views.penalties import PenaltyViewSet
from lego.apps.users.views.users import UsersViewSet

router = routers.DefaultRouter()
router.register(r'articles', ArticlesViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'events', EventViewSet, base_name='event')
router.register(r'events/(?P<event_pk>\d+)/pools', PoolViewSet)
router.register(r'events/(?P<event_pk>\d+)/registrations',
                RegistrationViewSet, base_name='registrations')
router.register(r'webhooks', StripeWebhook, base_name='webhooks')
router.register(r'groups', AbakusGroupViewSet)
router.register(r'interest-groups', InterestGroupViewSet)
router.register(r'meetings', MeetingViewSet)
router.register(r'meetings/(?P<meeting_pk>[^/]+)/invitations',
                MeetingInvitationViewSet, base_name='meeting-invitations')
router.register(r'memberships', MembershipViewSet)
router.register(r'notifications', NotificationFeedViewSet, base_name='feed-notifications')
router.register(r'oauth2/access-tokens', AccessTokenViewSet)
router.register(r'oauth2/applications', ApplicationViewSet)
router.register(r'pages', PageViewSet)
router.register(r'search/autocomplete', AutocompleteViewSet, base_name='autocomplete')
router.register(r'quotes', QuoteViewSet)
router.register(r'search/search', SearchViewSet, base_name='search')
router.register(r'users', UsersViewSet)
router.register(r'reactions', ReactionViewSet)
router.register(r'reaction_types', ReactionTypeViewSet)
router.register(r'penalties', PenaltyViewSet)
router.register(r'files', FileViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'companies/(?P<company_pk>[^/]+)/companyContact', CompanyContactViewSet)
router.register(r'companies/(?P<company_pk>[^/]+)/semesterStatuses', SemesterStatusViewSet)
