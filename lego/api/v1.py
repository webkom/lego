from django.urls import include, path
from rest_framework import routers

from lego.apps.achievements.views import LeaderBoardViewSet
from lego.apps.articles.views import ArticlesViewSet
from lego.apps.comments.views import CommentViewSet
from lego.apps.companies.views import (
    AdminCompanyViewSet,
    CompanyContactViewSet,
    CompanyFilesViewSet,
    CompanyInterestViewSet,
    CompanyViewSet,
    SemesterStatusViewSet,
    SemesterViewSet,
)
from lego.apps.contact.views import ContactFormViewSet
from lego.apps.email.views import EmailListViewSet, UserEmailViewSet
from lego.apps.emojis.views import EmojiViewSet
from lego.apps.events.views import (
    EventViewSet,
    PoolViewSet,
    RegistrationSearchViewSet,
    RegistrationViewSet,
)
from lego.apps.events.webhooks import StripeWebhook
from lego.apps.feeds.views import (
    NotificationsViewSet,
    PersonalFeedViewSet,
    UserFeedViewSet,
)
from lego.apps.files.views import FileViewSet
from lego.apps.flatpages.views import PageViewSet
from lego.apps.followers.views import (
    FollowCompanyViewSet,
    FollowEventViewSet,
    FollowUserViewSet,
)
from lego.apps.forums.views import ForumsViewSet, ThreadViewSet
from lego.apps.frontpage.views import FrontpageViewSet
from lego.apps.gallery.views import GalleryPictureViewSet, GalleryViewSet
from lego.apps.ical.viewsets import ICalTokenViewset, ICalViewset
from lego.apps.joblistings.views import JoblistingViewSet
from lego.apps.lending.views import LendableObjectViewSet
from lego.apps.meetings.views import (
    MeetingInvitationTokenViewSet,
    MeetingInvitationViewSet,
    MeetingViewSet,
)
from lego.apps.notifications.views import (
    AnnouncementViewSet,
    APNSDeviceViewSet,
    GCMDeviceViewSet,
    NotificationSettingsViewSet,
)
from lego.apps.oauth.views import AccessTokenViewSet, ApplicationViewSet
from lego.apps.podcasts.views import PodcastViewSet
from lego.apps.polls.views import PollViewSet
from lego.apps.quotes.views import QuoteViewSet
from lego.apps.reactions.views import ReactionViewSet
from lego.apps.restricted.views import RestrictedMailViewSet
from lego.apps.search.views import AutocompleteViewSet, SearchViewSet
from lego.apps.surveys.views import (
    SubmissionViewSet,
    SurveyTemplateViewSet,
    SurveyTokenViewset,
    SurveyViewSet,
)
from lego.apps.tags.views import TagViewSet
from lego.apps.users.views.abakus_groups import AbakusGroupViewSet
from lego.apps.users.views.membership_history import MembershipHistoryViewSet
from lego.apps.users.views.memberships import MembershipViewSet
from lego.apps.users.views.oidc import OIDCViewSet
from lego.apps.users.views.password_change import ChangePasswordViewSet
from lego.apps.users.views.password_reset import (
    PasswordResetPerformViewSet,
    PasswordResetRequestViewSet,
)
from lego.apps.users.views.penalties import PenaltyViewSet
from lego.apps.users.views.registration import UserRegistrationRequestViewSet
from lego.apps.users.views.user_delete import UserDeleteViewSet
from lego.apps.users.views.users import UsersViewSet
from lego.utils.views import SiteMetaViewSet

router = routers.DefaultRouter()
router.register(
    r"achievements/leaderboard", LeaderBoardViewSet, basename="achievements"
)
router.register(r"announcements", AnnouncementViewSet, basename="announcements")
router.register(r"articles", ArticlesViewSet)
router.register(r"bdb", AdminCompanyViewSet, basename="bdb")
router.register(r"calendar-ical", ICalViewset, basename="calendar-ical")
router.register(r"calendar-token", ICalTokenViewset, basename="calendar-token")
router.register(r"comments", CommentViewSet)
router.register(r"companies", CompanyViewSet)
router.register(
    r"companies/(?P<company_pk>\d+)/company-contacts",
    CompanyContactViewSet,
    basename="company-contact",
)
router.register(
    r"companies/(?P<company_pk>\d+)/files",
    CompanyFilesViewSet,
    basename="company-files",
)
router.register(
    r"companies/(?P<company_pk>\d+)/semester-statuses",
    SemesterStatusViewSet,
    basename="semester-status",
)
router.register(
    r"company-interests", CompanyInterestViewSet, basename="company-interest"
)
router.register(r"company-semesters", SemesterViewSet, basename="company-semester")
router.register(r"contact-form", ContactFormViewSet, basename="contact-form")
router.register(r"device-apns", APNSDeviceViewSet)
router.register(r"device-gcm", GCMDeviceViewSet)
router.register(r"email-lists", EmailListViewSet, basename="email-lists")
router.register(r"email-users", UserEmailViewSet, basename="email-users")
router.register(r"emojis", EmojiViewSet, basename="emoji")
router.register(r"events", EventViewSet, basename="event")
router.register(r"events/(?P<event_pk>\d+)/pools", PoolViewSet)
router.register(
    r"events/(?P<event_pk>\d+)/registration_search",
    RegistrationSearchViewSet,
    basename="registration-search",
)
router.register(
    r"events/(?P<event_pk>\d+)/registrations",
    RegistrationViewSet,
    basename="registrations",
)
router.register(
    r"feed-notifications", NotificationsViewSet, basename="feed-notifications"
)
router.register(r"feed-personal", PersonalFeedViewSet, basename="feed-personal")
router.register(r"feed-user/(?P<user_pk>\d+)", UserFeedViewSet, basename="feed-user")
router.register(r"files", FileViewSet)
router.register(r"followers-company", FollowCompanyViewSet)
router.register(r"followers-event", FollowEventViewSet)
router.register(r"followers-user", FollowUserViewSet)
router.register(r"forums", ForumsViewSet)
router.register(r"forums/(?P<forum_pk>\d+)/threads", ThreadViewSet)
router.register(r"frontpage", FrontpageViewSet, basename="frontpage")
router.register(r"galleries", GalleryViewSet)
router.register(r"galleries/(?P<gallery_pk>\d+)/pictures", GalleryPictureViewSet)
router.register(r"groups", AbakusGroupViewSet)
router.register(
    r"groups/(?P<group_pk>\d+)/memberships",
    MembershipViewSet,
    basename="abakusgroup-memberships",
)
router.register(r"joblistings", JoblistingViewSet, basename="joblisting")
router.register(r"lending/objects", LendableObjectViewSet, basename="lendable-object")
router.register(
    r"meeting-token", MeetingInvitationTokenViewSet, basename="meeting-token"
)
router.register(r"meetings", MeetingViewSet, basename="meeting")
router.register(
    r"meetings/(?P<meeting_pk>\d+)/invitations",
    MeetingInvitationViewSet,
    basename="meeting-invitations",
)
router.register(
    r"membership-history", MembershipHistoryViewSet, basename="membership-history"
)
router.register(
    r"notification-settings",
    NotificationSettingsViewSet,
    basename="notifications-settings",
)
router.register(
    r"oauth2-access-tokens", AccessTokenViewSet, basename="oauth2-access-tokens"
)
router.register(
    r"oauth2-applications", ApplicationViewSet, basename="oauth2-applications"
)
router.register(r"pages", PageViewSet)
router.register(r"password-change", ChangePasswordViewSet, basename="password-change")
router.register(
    r"password-reset-perform",
    PasswordResetPerformViewSet,
    basename="password-reset-perform",
)
router.register(
    r"password-reset-request",
    PasswordResetRequestViewSet,
    basename="password-reset-request",
)
router.register(r"penalties", PenaltyViewSet)
router.register(r"podcasts", PodcastViewSet, basename="podcasts")
router.register(r"polls", PollViewSet, basename="polls")
router.register(r"quotes", QuoteViewSet)
router.register(r"reactions", ReactionViewSet)
router.register(r"restricted-mail", RestrictedMailViewSet, basename="restricted-mail")
router.register(r"search-autocomplete", AutocompleteViewSet, basename="autocomplete")
router.register(r"search-search", SearchViewSet, basename="search")
router.register(r"site-meta", SiteMetaViewSet, basename="site-meta")
router.register(r"survey-results", SurveyTokenViewset, basename="survey-results")
router.register(r"survey-templates", SurveyTemplateViewSet, basename="survey-template")
router.register(r"surveys", SurveyViewSet)
router.register(
    r"surveys/(?P<survey_pk>\d+)/submissions", SubmissionViewSet, basename="submission"
)
router.register(r"tags", TagViewSet)
router.register(r"threads", ThreadViewSet)
router.register(r"user-delete", UserDeleteViewSet, basename="user-delete")
router.register(r"users", UsersViewSet)
router.register(
    r"users-registration-request",
    UserRegistrationRequestViewSet,
    basename="user-registration",
)
router.register(r"oidc", OIDCViewSet, basename="oidc")
router.register(r"webhooks-stripe", StripeWebhook, basename="webhooks-stripe")

urlpatterns = [
    path("", include(router.urls)),
]
