from rest_framework import routers

from lego.apps.articles.views import ArticlesViewSet
from lego.apps.comments.views import CommentViewSet
from lego.apps.companies.views import (CompanyContactViewSet, CompanyFilesViewSet,
                                       CompanyInterestViewSet, CompanyViewSet,
                                       SemesterStatusViewSet, SemesterViewSet)
from lego.apps.contact.views import ContactFormViewSet
from lego.apps.email.views import AbakusGroupEmailViewSet, EmailListViewSet, UserEmailViewSet
from lego.apps.events.views import EventViewSet, PoolViewSet, RegistrationViewSet
from lego.apps.events.webhooks import StripeWebhook
from lego.apps.feed.views import (CompanyFeedViewSet, GroupFeedViewSet, NotificationFeedViewSet,
                                  PersonalFeedViewSet, UserFeedViewSet)
from lego.apps.files.views import FileViewSet
from lego.apps.flatpages.views import PageViewSet
from lego.apps.followers.views import FollowCompanyViewSet, FollowEventViewSet, FollowUserViewSet
from lego.apps.gallery.views import GalleryPictureViewSet, GalleryViewSet
from lego.apps.ical.viewsets import ICalTokenViewset, ICalViewset
from lego.apps.joblistings.views import JoblistingViewSet
from lego.apps.meetings.views import (MeetingInvitationTokenViewSet, MeetingInvitationViewSet,
                                      MeetingViewSet)
from lego.apps.notifications.views import (AnnouncementViewSet, APNSDeviceViewSet, GCMDeviceViewSet,
                                           NotificationSettingsViewSet)
from lego.apps.oauth.views import AccessTokenViewSet, ApplicationViewSet
from lego.apps.quotes.views import QuoteViewSet
from lego.apps.reactions.views import ReactionTypeViewSet, ReactionViewSet
from lego.apps.restricted.views import RestrictedMailViewSet
from lego.apps.search.views import AutocompleteViewSet, SearchViewSet
from lego.apps.slack.views import SlackInviteViewSet
from lego.apps.users.views.abakus_groups import AbakusGroupViewSet
from lego.apps.users.views.memberships import MembershipViewSet
from lego.apps.users.views.password_change import ChangePasswordViewSet
from lego.apps.users.views.password_reset import (PasswordResetPerformViewSet,
                                                  PasswordResetRequestViewSet)
from lego.apps.users.views.penalties import PenaltyViewSet
from lego.apps.users.views.registration import UserRegistrationRequestViewSet
from lego.apps.users.views.student_confirmation import (StudentConfirmationPerformViewSet,
                                                        StudentConfirmationRequestViewSet)
from lego.apps.users.views.users import UsersViewSet
from lego.utils.views import SiteMetaViewSet

router = routers.DefaultRouter()
router.register(r'articles', ArticlesViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'companies/(?P<company_pk>\d+)/company-contacts',
                CompanyContactViewSet, base_name='company-contact')
router.register(r'companies/(?P<company_pk>\d+)/semester-statuses',
                SemesterStatusViewSet, base_name='semester-status')
router.register(r'companies/(?P<company_pk>\d+)/files',
                CompanyFilesViewSet, base_name='company-files')
router.register(r'company-interests', CompanyInterestViewSet, base_name='company-interest')
router.register(r'company-semesters', SemesterViewSet)
router.register(r'events', EventViewSet, base_name='event')
router.register(r'events/(?P<event_pk>\d+)/pools', PoolViewSet)
router.register(r'events/(?P<event_pk>\d+)/registrations',
                RegistrationViewSet, base_name='registrations')
router.register(r'webhooks-stripe', StripeWebhook, base_name='webhooks-stripe')
router.register(r'groups', AbakusGroupViewSet)
router.register(r'meetings', MeetingViewSet)
router.register(r'meetings/(?P<meeting_pk>\d+)/invitations',
                MeetingInvitationViewSet, base_name='meeting-invitations')
router.register(r'meeting-token',
                MeetingInvitationTokenViewSet, base_name='meeting-token')
router.register(r'memberships', MembershipViewSet)
router.register(
    r'notification-settings', NotificationSettingsViewSet, base_name='notifications-settings'
)
router.register(r'joblistings', JoblistingViewSet, base_name='joblisting')
router.register(r'oauth2-access-tokens', AccessTokenViewSet, base_name='oauth2-access-tokens')
router.register(r'oauth2-applications', ApplicationViewSet, base_name='oauth2-applications')
router.register(r'pages', PageViewSet)
router.register(r'search-autocomplete', AutocompleteViewSet, base_name='autocomplete')
router.register(r'quotes', QuoteViewSet)
router.register(r'search-search', SearchViewSet, base_name='search')
router.register(
    r'users-registration-request',
    UserRegistrationRequestViewSet,
    base_name='user-registration'
)
router.register(
    r'users-student-confirmation-request',
    StudentConfirmationRequestViewSet,
    base_name='student-confirmation-request'
)
router.register(
    r'users-student-confirmation-perform',
    StudentConfirmationPerformViewSet,
    base_name='student-confirmation-perform'
)
router.register(r'users', UsersViewSet)
router.register(r'password-reset-request', PasswordResetRequestViewSet,
                base_name='password-reset-request')
router.register(r'password-reset-perform', PasswordResetPerformViewSet,
                base_name='password-reset-perform')
router.register(r'password-change', ChangePasswordViewSet, base_name='password-change')
router.register(r'reactions', ReactionViewSet)
router.register(r'reaction-types', ReactionTypeViewSet)
router.register(r'restricted-mail', RestrictedMailViewSet, base_name='restricted-mail')
router.register(r'penalties', PenaltyViewSet)
router.register(r'files', FileViewSet)
router.register(r'followers-user', FollowUserViewSet)
router.register(r'followers-event', FollowEventViewSet)
router.register(r'followers-company', FollowCompanyViewSet)
router.register(r'feed-user', UserFeedViewSet, base_name='feed-user')
router.register(r'feed-personal', PersonalFeedViewSet, base_name='feed-personal')
router.register(r'feed-notifications', NotificationFeedViewSet, base_name='feed-notifications')
router.register(r'feed-group', GroupFeedViewSet, base_name='feed-group')
router.register(r'feed-company', CompanyFeedViewSet, base_name='feed-company')
router.register(r'slack-invite', SlackInviteViewSet, base_name='slack-invite')
router.register(r'calendar-ical', ICalViewset, base_name='calendar-ical')
router.register(r'calendar-token', ICalTokenViewset, base_name='calendar-token')
router.register(r'device-apns', APNSDeviceViewSet)
router.register(r'device-gcm', GCMDeviceViewSet)
router.register(r'galleries', GalleryViewSet)
router.register(r'galleries/(?P<gallery_pk>\d+)/pictures', GalleryPictureViewSet)
router.register(r'announcements', AnnouncementViewSet, base_name='announcements')
router.register(r'email-lists', EmailListViewSet, base_name='email-lists')
router.register(r'email-users', UserEmailViewSet, base_name='email-users')
router.register(r'email-groups', AbakusGroupEmailViewSet, base_name='email-groups')
router.register(r'contact-form', ContactFormViewSet, base_name='contact-form')
router.register(r'site-meta', SiteMetaViewSet, base_name='site-meta')
