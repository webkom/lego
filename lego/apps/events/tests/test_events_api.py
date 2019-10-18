from copy import deepcopy
from datetime import timedelta
from unittest import mock, skipIf

from django.urls import reverse
from django.utils import timezone

import stripe
from djangorestframework_camel_case.render import camelize

from lego.apps.events import constants
from lego.apps.events.exceptions import (
    UnansweredSurveyException,
    WebhookDidNotFindRegistration,
)
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.tasks import stripe_webhook_event
from lego.apps.events.tests.utils import get_dummy_users
from lego.apps.surveys.models import Submission, Survey
from lego.apps.users.constants import GROUP_GRADE
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase, BaseAPITransactionTestCase

from .utils import create_token

_test_event_data = [
    {
        "title": "Event1",
        "description": "Ingress1",
        "text": "Ingress1",
        "eventType": "event",
        "eventStatusType": "NORMAL",
        "location": "F252",
        "startTime": "2011-09-01T13:20:30Z",
        "endTime": "2012-09-01T13:20:30Z",
        "mergeTime": "2012-01-01T13:20:30Z",
        "isAbakomOnly": False,
        "pools": [
            {
                "name": "Initial Pool",
                "capacity": 10,
                "activationDate": "2012-09-01T10:20:30Z",
                "permissionGroups": [1],
            }
        ],
    },
    {
        "title": "Event2",
        "description": "Ingress2",
        "text": "Ingress2",
        "eventType": "event",
        "eventStatusType": "NORMAL",
        "location": "F252",
        "startTime": "2015-09-01T13:20:30Z",
        "endTime": "2015-09-01T13:20:30Z",
        "mergeTime": "2016-01-01T13:20:30Z",
        "isAbakomOnly": True,
        "pools": [
            {
                "name": "Initial Pool 1",
                "capacity": 10,
                "activationDate": "2012-09-01T10:20:30Z",
                "permissionGroups": [2],
            },
            {
                "name": "Initial Pool 2",
                "capacity": 20,
                "activationDate": "2012-09-01T10:20:30Z",
                "permissionGroups": [2],
            },
        ],
    },
    {
        "title": "Event3",
        "description": "Ingress3",
        "text": "Ingress3",
        "eventType": "event",
        "eventStatusType": "TBA",
        "location": "F252",
        "startTime": "2015-09-01T13:20:30Z",
        "endTime": "2015-09-01T13:20:30Z",
        "mergeTime": "2016-01-01T13:20:30Z",
        "isAbakomOnly": True,
        "pools": [
            {
                "name": "Initial Pool 1",
                "capacity": 10,
                "activationDate": "2012-09-01T10:20:30Z",
                "permissionGroups": [2],
            }
        ],
    },
    {
        "title": "Event4",
        "description": "Ingress4",
        "text": "Ingress4",
        "eventType": "event",
        "eventStatusType": "OPEN",
        "location": "F252",
        "startTime": "2015-09-01T13:20:30Z",
        "endTime": "2015-09-01T13:20:30Z",
        "mergeTime": "2016-01-01T13:20:30Z",
        "isAbakomOnly": True,
        "pools": [
            {
                "name": "Initial Pool 1",
                "capacity": 10,
                "activationDate": "2012-09-01T10:20:30Z",
                "permissionGroups": [2],
            }
        ],
    },
    {
        "title": "Event5",
        "description": "Ingress5",
        "text": "Ingress5",
        "eventType": "event",
        "eventStatusType": "INFINITE",
        "location": "F252",
        "startTime": "2015-09-01T13:20:30Z",
        "endTime": "2015-09-01T13:20:30Z",
        "mergeTime": "2016-01-01T13:20:30Z",
        "isAbakomOnly": True,
        "pools": [
            {
                "name": "Initial Pool 1",
                "capacity": 10,
                "activationDate": "2012-09-01T10:20:30Z",
                "permissionGroups": [2],
            }
        ],
    },
    {
        "title": "Event6",
        "description": "Ingress6",
        "text": "Ingress6",
        "eventType": "event",
        "location": "F252",
        "startTime": "2015-09-01T13:20:30Z",
        "endTime": "2015-09-01T13:20:30Z",
        "mergeTime": "2016-01-01T13:20:30Z",
        "isAbakomOnly": True,
        "pools": [
            {
                "name": "Initial Pool 1",
                "capacity": 10,
                "activationDate": "2012-09-01T10:20:30Z",
                "permissionGroups": [2],
            }
        ],
    },
]

_test_pools_data = [
    {
        "name": "TESTPOOL1",
        "capacity": 10,
        "activationDate": "2012-09-01T10:20:30Z",
        "permissionGroups": [1],
    },
    {
        "name": "TESTPOOL2",
        "capacity": 20,
        "activationDate": "2012-09-02T11:20:30Z",
        "permissionGroups": [10],
    },
    {
        "name": "TESTPOOL3",
        "capacity": 30,
        "activationDate": "2012-09-02T12:20:30Z",
        "permissionGroups": [1],
    },
]

_test_registration_data = {"user": 1}


def _get_list_url():
    return reverse("api:v1:event-list")


def _get_detail_url(pk):
    return reverse("api:v1:event-detail", kwargs={"pk": pk})


def _get_pools_list_url(event_pk):
    return reverse("api:v1:pool-list", kwargs={"event_pk": event_pk})


def _get_pools_detail_url(event_pk, pool_pk):
    return reverse("api:v1:pool-detail", kwargs={"event_pk": event_pk, "pk": pool_pk})


def _get_registrations_list_url(event_pk):
    return reverse("api:v1:registrations-list", kwargs={"event_pk": event_pk})


def _get_registrations_detail_url(event_pk, registration_pk):
    return reverse(
        "api:v1:registrations-detail",
        kwargs={"event_pk": event_pk, "pk": registration_pk},
    )


def _get_registration_search_url(event_pk):
    return reverse("api:v1:registration-search-list", kwargs={"event_pk": event_pk})


def _get_upcoming_url():
    return reverse("api:v1:event-upcoming")


class ListEventsTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_users.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        date = timezone.now().replace(hour=16, minute=15, second=0, microsecond=0)
        for event in Event.objects.all():
            event.start_time = date + timedelta(days=10)
            event.end_time = date + timedelta(days=10, hours=4)
            event.save()

    def test_with_unauth(self):
        event_response = self.client.get(_get_list_url())
        self.assertEqual(event_response.status_code, 200)
        self.assertEqual(len(event_response.json()["results"]), 5)

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_list_url())
        self.assertEqual(event_response.status_code, 200)
        self.assertEqual(len(event_response.json()["results"]), 5)

    def test_with_webkom_user(self):
        AbakusGroup.objects.get(name="Webkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_list_url())
        self.assertEqual(event_response.status_code, 200)
        self.assertEqual(len(event_response.json()["results"]), 9)


class RetrieveEventsTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_users.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_without_authentication(self):
        """Test that unauth user can retrieve event"""
        event_response = self.client.get(_get_detail_url(2))
        self.assertEqual(event_response.status_code, 200)

    def test_with_authentication(self):
        """Test that auth user can retrieve event"""
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(2))
        self.assertEqual(event_response.status_code, 200)

    def test_unauth_cant_see_registrations(self):
        event_response = self.client.get(_get_detail_url(1))
        for pool in event_response.json()["pools"]:
            self.assertIsNone(pool.get("registrations", None))

    def test_auth_cant_see_registrations(self):
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(1))
        for pool in event_response.json()["pools"]:
            self.assertIsNone(pool.get("registrations", None))

    def test_abakus_see_registrations(self):
        """Tests that a user that is allowed to register for the event can see the registrations"""
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(1))
        for pool in event_response.json()["pools"]:
            self.assertIsNotNone(pool.get("registrations", None))

    def test_creator_see_registrations(self):
        self.client.force_authenticate(self.abakus_user)
        event = Event.objects.get(id=1)
        event.created_by = self.abakus_user
        event.save()
        event_response = self.client.get(_get_detail_url(1))
        for pool in event_response.json()["pools"]:
            self.assertIsNotNone(pool.get("registrations", None))

    def test_without_auth_permission_abakom_only(self):
        """Test that unauth user cannot retrieve abakom only event"""
        event = Event.objects.get(title="ABAKOM_ONLY")
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(event.id))
        self.assertEqual(event_response.status_code, 404)

    def test_without_group_permission_abakom_only(self):
        """Test that auth user cannot retrieve abakom only event"""
        event = Event.objects.get(title="ABAKOM_ONLY")
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(event.id))
        self.assertEqual(event_response.status_code, 404)

    def test_with_group_permission_abakom_only(self):
        """Test that abakom user can retrieve abakom only event"""
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        event = Event.objects.get(title="ABAKOM_ONLY")
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(event.id))
        self.assertEqual(event_response.status_code, 200)

    def test_payment_status_hidden_when_not_priced(self):
        """Test that paymentStatus is hidden when getting nonpriced event"""
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(1))

        for pool in event_response.json()["pools"]:
            for reg in pool["registrations"]:
                with self.assertRaises(KeyError):
                    reg["paymentStatus"]

    def test_only_own_fields_visible(self):
        """Test that a user can only view own fields"""
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(5))

        for pool in event_response.json()["pools"]:
            for reg in pool["registrations"]:
                if reg["user"]["id"] == self.abakus_user.id:
                    self.assertIsNotNone(reg["feedback"])
                    self.assertIsNotNone(reg["paymentStatus"])
                else:
                    self.assertIsNone(reg["feedback"])
                    self.assertIsNone(reg["paymentStatus"])

    def test_event_registration_no_shared_memberships(self):
        """Test registrations shared_memberships without any shared groups"""
        self.client.force_authenticate(self.abakus_user)

        event_response = self.client.get(_get_detail_url(5))
        memberships = [
            reg["sharedMemberships"]
            for reg in event_response.json()["pools"][0]["registrations"]
        ]
        self.assertEqual(memberships, [0, 0, 0])

    def test_event_registration_shared_membership_count(self):
        """Test registrations shared_memberships"""
        auth_user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Webkom").add_user(auth_user)
        self.client.force_authenticate(auth_user)
        event = Event.objects.get(pk=5)
        group1 = AbakusGroup.objects.create(name="DummyGroup1", type=GROUP_GRADE)
        group2 = AbakusGroup.objects.create(name="DummyGroup2", type=GROUP_GRADE)
        reg1, reg2, reg3 = event.registrations.all().order_by("id")[:3]

        group1.add_user(auth_user)
        group1.add_user(reg3.user)
        group1.add_user(reg1.user)
        group2.add_user(auth_user)
        group2.add_user(reg3.user)

        shared_memberships_count = {reg1.id: 1, reg2.id: 0, reg3.id: 2}

        event_response = self.client.get(_get_detail_url(5))

        registrations = event_response.json()["pools"][0]["registrations"]

        for reg in registrations:
            reg_id = reg["id"]
            self.assertEqual(
                reg["sharedMemberships"],
                shared_memberships_count[reg_id],
                f'Wrong count for registration id "{reg_id}"',
            )

    def unanswered_surveys_setup(self):
        user = User.objects.all().first()
        AbakusGroup.objects.get(name="Webkom").add_user(user)
        AbakusGroup.objects.get(pk=1).add_user(user)
        self.client.force_authenticate(user=user)

        response = self.client.post(_get_list_url(), _test_event_data[0])
        event = Event.objects.get(pk=response.json().get("id"))
        event.start_time = timezone.now() + timedelta(hours=3)
        event.save()
        return user, event

    def test_not_attending_means_no_unanswered_survey(self):
        """Test that not attending an event means you don't get an unanswered survey"""
        user, event = self.unanswered_surveys_setup()

        Survey.objects.create(event=event)
        Registration.objects.create(event=event, user=user, presence=constants.UNKNOWN)
        Registration.objects.create(
            event=event, user=User.objects.get(pk=2), presence=constants.PRESENT
        )
        self.client.get(_get_detail_url(event.id))
        unanswered_surveys = user.unanswered_surveys()
        self.assertEqual(len(unanswered_surveys), 0)

    def test_no_unanswered_surveys_means_you_can_register(self):
        """Test that having no unanswered surveys means you can register for events"""
        user, event = self.unanswered_surveys_setup()

        self.client.get(_get_detail_url(event.id))
        event.register(Registration.objects.get_or_create(event=event, user=user)[0])
        self.assertEqual(event.number_of_registrations, 1)

    def test_attending_means_you_get_unanswered_survey(self):
        """Test that attending an event means you do get an unanswered survey"""
        user, event = self.unanswered_surveys_setup()

        Registration.objects.create(event=event, user=user, presence=constants.PRESENT)
        survey = Survey.objects.create(event=event)
        self.client.get(_get_detail_url(event.id))
        unanswered_surveys = user.unanswered_surveys()
        self.assertEqual([survey.id], unanswered_surveys)

    def unanswered_surveys_wont_let_you_register(self):
        """Test that having an unanswered survey means you can't register for events"""
        user, event = self.unanswered_surveys_setup()

        Registration.objects.create(event=event, user=user, presence=constants.PRESENT)
        Survey.objects.create(event=event)
        self.client.get(_get_detail_url(event.id))

        with self.assertRaises(UnansweredSurveyException):
            event.register(
                Registration.objects.get_or_create(event=event, user=user)[0]
            )

    def test_answering_survey_lets_you_register(self):
        """Test that answering the survey lets you register again"""
        user, event = self.unanswered_surveys_setup()

        Registration.objects.create(event=event, user=user, presence=constants.PRESENT)
        survey = Survey.objects.create(event=event)
        self.client.get(_get_detail_url(event.id))

        Submission.objects.create(user=user, survey=survey)
        self.client.get(_get_detail_url(event.id))
        unanswered_surveys = user.unanswered_surveys()
        self.assertEqual(len(unanswered_surveys), 0)

        event.register(Registration.objects.get_or_create(event=event, user=user)[0])
        self.assertEqual(event.number_of_registrations, 1)


class CreateEventsTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_users.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        AbakusGroup.objects.get(name="Webkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        self.event_response = self.client.post(_get_list_url(), _test_event_data[0])
        self.assertEqual(self.event_response.status_code, 201)
        self.event_id = self.event_response.json().pop("id", None)

    def test_event_creation(self):
        """Test event creation with pools"""
        self.assertIsNotNone(self.event_id)
        self.assertEqual(self.event_response.status_code, 201)
        res_event = self.event_response.json()
        expect_event = camelize(_test_event_data[0])
        for key in [
            "title",
            "description",
            "text",
            "startTime",
            "endTime",
            "mergeTime",
            "isAbakomOnly",
        ]:
            self.assertEqual(res_event[key], expect_event[key])
        created_event = Event.objects.get(id=self.event_id)
        self.assertFalse(created_event.require_auth)
        self.assertEqual(created_event.can_view_groups.count(), 0)

        expect_pools = camelize(expect_event["pools"])
        res_pools = res_event["pools"]
        for i in range(len(expect_pools)):
            self.assertIsNotNone(res_pools[i].pop("id"))
            for key in ["name", "capacity", "activationDate", "permissionGroups"]:
                self.assertEqual(res_pools[i][key], expect_pools[i][key])

    def test_event_creation_tba(self):
        """Test event creation for TBA status type"""
        self.event_response = self.client.post(_get_list_url(), _test_event_data[2])
        self.assertEqual(self.event_response.status_code, 201)
        event_id = self.event_response.json().pop("id", None)
        self.assertIsNotNone(event_id)
        res_event = self.event_response.json()
        expect_event = _test_event_data[2]
        for key in [
            "title",
            "description",
            "text",
            "startTime",
            "endTime",
            "mergeTime",
            "isAbakomOnly",
        ]:
            self.assertEqual(res_event[key], expect_event[key])
        created_event = Event.objects.get(id=event_id)
        self.assertEqual(created_event.event_status_type, "TBA")
        self.assertEqual(created_event.location, "TBA")
        self.assertEqual(len(created_event.pools.all()), 0)

    def test_event_creation_open(self):
        """Test event creation for OPEN status type"""
        self.event_response = self.client.post(_get_list_url(), _test_event_data[3])
        self.assertEqual(self.event_response.status_code, 201)
        self.event_id = self.event_response.json().pop("id", None)
        self.assertIsNotNone(self.event_id)
        res_event = self.event_response.json()
        expect_event = _test_event_data[3]
        for key in [
            "title",
            "description",
            "text",
            "startTime",
            "location",
            "endTime",
            "mergeTime",
            "isAbakomOnly",
        ]:
            self.assertEqual(res_event[key], expect_event[key])
        created_event = Event.objects.get(id=self.event_id)
        self.assertEqual(created_event.event_status_type, "OPEN")
        self.assertEqual(len(created_event.pools.all()), 0)

    def test_event_creation_infinite(self):
        """Test event creation for INFINITE status type"""
        self.event_response = self.client.post(_get_list_url(), _test_event_data[4])
        self.assertEqual(self.event_response.status_code, 201)
        self.event_id = self.event_response.json().pop("id", None)
        self.assertIsNotNone(self.event_id)
        res_event = self.event_response.json()
        expect_event = _test_event_data[4]
        for key in [
            "title",
            "description",
            "text",
            "startTime",
            "location",
            "endTime",
            "mergeTime",
            "isAbakomOnly",
        ]:
            self.assertEqual(res_event[key], expect_event[key])
        created_event = Event.objects.get(id=self.event_id)
        self.assertEqual(created_event.event_status_type, "INFINITE")
        self.assertEqual(len(created_event.pools.all()), 1)
        self.assertEqual(created_event.pools.first().capacity, 0)

    def test_event_create_no_event_status_type(self):
        """Test event creation with no event status type posted"""
        event_response = self.client.post(_get_list_url(), _test_event_data[5])
        self.assertEqual(event_response.status_code, 201)
        event_id = event_response.json().pop("id", None)
        self.assertIsNotNone(event_id)
        created_event = Event.objects.get(id=event_id)
        self.assertEqual(created_event.event_status_type, "TBA")

    def test_event_creation_without_auth(self):
        self.client.logout()
        response = self.client.post(_get_list_url(), _test_event_data[1])
        self.assertEqual(response.status_code, 401)

    def test_event_creation_without_perm(self):
        user = User.objects.get(username="abakule")
        self.client.force_authenticate(user)
        response = self.client.post(_get_list_url(), _test_event_data[1])
        self.assertEqual(response.status_code, 403)

    def test_event_update(self):
        """Test updating event attributes"""
        expect_event = _test_event_data[1].copy()
        expect_event.pop("pools")
        event_update_response = self.client.put(
            _get_detail_url(self.event_id), expect_event
        )
        self.assertEqual(event_update_response.status_code, 200)
        self.assertEqual(self.event_id, event_update_response.json().pop("id"))
        res_event = event_update_response.json()
        for key in [
            "title",
            "description",
            "text",
            "startTime",
            "endTime",
            "mergeTime",
            "isAbakomOnly",
        ]:
            self.assertEqual(res_event[key], expect_event[key])
        updated_event = Event.objects.get(id=self.event_id)
        abakom_group = AbakusGroup.objects.get(name="Abakom")
        self.assertTrue(updated_event.require_auth)
        self.assertEqual(updated_event.can_view_groups.count(), 1)
        self.assertEqual(updated_event.can_view_groups.first(), abakom_group)

    def test_event_update_without_perm(self):
        """Test updating event attributes without permissions is not allowed"""
        user = User.objects.get(username="abakule")
        self.client.force_authenticate(user)
        try_event = _test_event_data[1].copy()
        try_event.pop("pools")
        event_update_response = self.client.put(
            _get_detail_url(self.event_id), try_event
        )
        self.assertEqual(event_update_response.status_code, 403)

    def test_event_update_without_auth(self):
        """Test updating event attributes without auth is not allowed"""
        self.client.logout()
        try_event = _test_event_data[1].copy()
        try_event.pop("pools")
        event_update_response = self.client.put(
            _get_detail_url(self.event_id), try_event
        )
        self.assertEqual(event_update_response.status_code, 401)

    def test_event_partial_update(self):
        """Test patching event attributes"""
        expect_event = _test_event_data[0]
        event_update_response = self.client.patch(
            _get_detail_url(self.event_id), {"title": "PATCHED"}
        )
        self.assertEqual(event_update_response.status_code, 200)
        self.assertEqual(self.event_id, event_update_response.json().pop("id"))
        res_event = event_update_response.json()
        self.assertEqual(res_event["title"], "PATCHED")
        for key in [
            "description",
            "text",
            "startTime",
            "endTime",
            "mergeTime",
            "isAbakomOnly",
        ]:
            self.assertEqual(res_event[key], expect_event[key])
        event = Event.objects.get(id=self.event_id)
        self.assertEqual(0, event.can_view_groups.count())

    def test_event_update_with_pool_creation(self):
        """Test updating event attributes and add a pool"""
        expect_event = _test_event_data[1]
        expect_event["pools"] = self.event_response.json().get("pools") + [
            _test_pools_data[0]
        ]
        event_update_response = self.client.put(
            _get_detail_url(self.event_id), expect_event
        )
        self.assertEqual(event_update_response.status_code, 200)
        self.assertEqual(self.event_id, event_update_response.json().pop("id"))
        res_event = event_update_response.json()
        for key in [
            "title",
            "description",
            "text",
            "startTime",
            "endTime",
            "mergeTime",
            "isAbakomOnly",
        ]:
            self.assertEqual(res_event[key], expect_event[key])

        # These are not sorted due to id not present on new pool
        # camelize() because nested serializer (pool) camelizes output
        expect_pools = sorted(
            camelize(expect_event["pools"]), key=lambda pool: pool["name"]
        )
        res_pools = sorted(res_event["pools"], key=lambda pool: pool["name"])
        for i in range(len(expect_pools)):
            self.assertIsNotNone(res_pools[i].pop("id"))
            for key in ["name", "capacity", "activationDate", "permissionGroups"]:
                self.assertEqual(res_pools[i][key], expect_pools[i][key])

    def test_event_update_with_pool_deletion(self):
        """Test that pool updated through event is deleted"""
        _test_event_data[1]["pools"] = [_test_pools_data[0]]
        event_update_response = self.client.put(
            _get_detail_url(self.event_id), _test_event_data[1]
        )

        self.assertEqual(event_update_response.status_code, 200)
        res_event = event_update_response.json()
        expect_event = _test_event_data[1]
        for key in [
            "title",
            "description",
            "text",
            "startTime",
            "endTime",
            "mergeTime",
            "isAbakomOnly",
        ]:
            self.assertEqual(res_event[key], expect_event[key])

        expect_pools = camelize(expect_event["pools"])
        res_pools = res_event["pools"]
        for i in range(len(expect_pools)):
            self.assertIsNotNone(res_pools[i].pop("id"))
            for key in ["name", "capacity", "activationDate", "permissionGroups"]:
                self.assertEqual(res_pools[i][key], expect_pools[i][key])

    def test_event_partial_update_pool_deletion(self):
        """Test that all pools are deleted when patching"""
        event_update_response = self.client.patch(
            _get_detail_url(self.event_id), {"pools": []}
        )

        self.assertEqual(event_update_response.status_code, 200)
        res_event = event_update_response.json()
        expect_event = _test_event_data[0]
        for key in [
            "title",
            "description",
            "text",
            "startTime",
            "endTime",
            "mergeTime",
            "isAbakomOnly",
        ]:
            self.assertEqual(res_event[key], expect_event[key])
        event = Event.objects.get(id=self.event_id)
        self.assertEqual(0, event.can_view_groups.count())
        self.assertEqual(res_event["pools"], [])

    def test_event_correct_youtube_url(self):
        test_event = _test_event_data[0].copy()
        test_event["youtubeUrl"] = "https://www.youtube.com/watch?v=KrzIaRwAMvc"
        self.response = self.client.post(_get_list_url(), test_event)
        self.assertEqual(self.response.status_code, 201)

    def test_event_wrong_youtube_url(self):
        test_event = _test_event_data[0].copy()
        test_event["youtubeUrl"] = "skra"
        self.response = self.client.post(_get_list_url(), test_event)
        self.assertEqual(self.response.status_code, 400)


class PoolsTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_users.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_create_pool(self):
        AbakusGroup.objects.get(name="Webkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.post(_get_pools_list_url(1), _test_pools_data[0])
        self.assertEqual(pool_response.status_code, 201)

    def test_create_pool_as_bedkom(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.post(_get_pools_list_url(1), _test_pools_data[0])
        self.assertEqual(pool_response.status_code, 201)

    def test_create_failing_pool_as_abakus(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.post(_get_pools_list_url(1), _test_pools_data[0])
        self.assertEqual(pool_response.status_code, 403)

    def test_delete_pool_with_registrations_as_admin(self):
        """Test that pool deletion is not possible when registrations are attached"""
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.delete(_get_pools_detail_url(1, 1))
        self.assertEqual(pool_response.status_code, 409)

    def test_delete_pool_without_registrations_as_admin(self):
        """Test that pool deletion is possible without attached registrations"""
        pool = Pool.objects.create(
            name="Testpool", event_id=1, activation_date=timezone.now()
        )
        pool.permission_groups.set([1, 2])
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.delete(_get_pools_detail_url(1, pool.id))
        self.assertEqual(pool_response.status_code, 204)

    def test_delete_pool_without_registrations_as_abakus(self):
        """Test that abakususer cannot delete pool"""
        pool = Pool.objects.create(
            name="Testpool", event_id=1, activation_date=timezone.now()
        )
        pool.permission_groups.set([1, 2])
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.delete(_get_pools_detail_url(1, pool.id))
        self.assertEqual(pool_response.status_code, 403)


@mock.patch("lego.apps.events.views.verify_captcha", return_value=True)
class RegistrationsTransactionTestCase(BaseAPITransactionTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_users.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        Event.objects.all().update(start_time=timezone.now() + timedelta(hours=3))
        self.abakus_user = User.objects.get(pk=1)
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)

    def test_create(self, *args):
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {}
        )
        self.assertEqual(registration_response.status_code, 202)
        self.assertEqual(
            registration_response.json().get("status"), constants.PENDING_REGISTER
        )
        res = self.client.get(
            _get_registrations_detail_url(event.id, registration_response.json()["id"])
        )
        registration = Registration.objects.get(id=res.json()["id"])
        self.assertEqual(registration.created_by.id, res.json()["user"]["id"])
        self.assertEqual(registration.updated_by.id, res.json()["user"]["id"])
        self.assertEqual(res.json()["user"]["id"], 1)
        self.assertEqual(res.json()["status"], constants.SUCCESS_REGISTER)

    def test_register_tba_event(self, *args):
        event = Event.objects.get(title="TBA_EVENT")
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {}
        )
        self.assertEqual(registration_response.status_code, 202)
        self.assertEqual(
            registration_response.json().get("status"), constants.PENDING_REGISTER
        )
        res = self.client.get(
            _get_registrations_detail_url(event.id, registration_response.json()["id"])
        )
        self.assertEqual(res.json()["user"]["id"], 1)
        self.assertEqual(res.json()["status"], constants.FAILURE_REGISTER)

    def test_register_open_event(self, *args):
        event = Event.objects.get(title="OPEN_EVENT")
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {}
        )
        self.assertEqual(registration_response.status_code, 202)
        self.assertEqual(
            registration_response.json().get("status"), constants.PENDING_REGISTER
        )
        res = self.client.get(
            _get_registrations_detail_url(event.id, registration_response.json()["id"])
        )
        self.assertEqual(res.json()["user"]["id"], 1)
        self.assertEqual(res.json()["status"], constants.FAILURE_REGISTER)

    def test_register_open_infinite(self, *args):
        event = Event.objects.get(title="INFINITE_EVENT")
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {}
        )
        self.assertEqual(registration_response.status_code, 202)
        self.assertEqual(
            registration_response.json().get("status"), constants.PENDING_REGISTER
        )
        res = self.client.get(
            _get_registrations_detail_url(event.id, registration_response.json()["id"])
        )
        self.assertEqual(res.json()["user"]["id"], 1)
        self.assertEqual(res.json()["status"], constants.SUCCESS_REGISTER)

    def test_register_no_pools(self, *args):
        event = Event.objects.get(title="NO_POOLS_ABAKUS")
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {}
        )
        self.assertEqual(registration_response.status_code, 202)
        self.assertEqual(
            registration_response.json().get("status"), constants.PENDING_REGISTER
        )
        res = self.client.get(
            _get_registrations_detail_url(event.id, registration_response.json()["id"])
        )
        self.assertEqual(res.json()["status"], constants.FAILURE_REGISTER)

    def test_unregister(self, *args):
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        registration = Registration.objects.get(user=self.abakus_user, event=event)
        registration_response = self.client.delete(
            _get_registrations_detail_url(event.id, registration.id)
        )

        get_unregistered = self.client.get(
            _get_registrations_detail_url(event.id, registration.id)
        )
        self.assertEqual(registration_response.status_code, 202)
        self.assertEqual(get_unregistered.status_code, 200)
        self.assertEqual(get_unregistered.json().get("updatedBy"), self.abakus_user.id)
        self.assertIsNone(get_unregistered.json().get("pool"))


@mock.patch("lego.apps.events.views.verify_captcha", return_value=True)
class RegistrationsTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_users.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        Event.objects.all().update(start_time=timezone.now() + timedelta(hours=3))
        self.abakus_user = User.objects.get(pk=1)
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)

    def test_unable_to_create(self, *args):
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        self.non_abakus_user = User.objects.get(pk=2)
        AbakusGroup.objects.get(name="Users").add_user(self.non_abakus_user)
        self.client.force_authenticate(self.non_abakus_user)
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {}
        )
        self.assertEqual(registration_response.status_code, 403)

    def test_update_feedback(self, *args):
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {}
        )
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.json()["id"]),
            {"feedback": "UPDATED"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["feedback"], "UPDATED")

    def test_update_presence_without_permission(self, *args):
        """ Test that abakus user cannot update presence """
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {}
        )
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.json()["id"]),
            {"presence": "PRESENT"},
        )
        self.assertEqual(res.status_code, 403)

    def test_update_presence_with_permission(self, *args):
        """ Test that admin can update presence """
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {}
        )
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.json()["id"]),
            {"presence": "PRESENT"},
        )
        registration = Registration.objects.get(id=res.json()["id"])
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["presence"], "PRESENT")
        self.assertEqual(registration.updated_by, self.abakus_user)

    def test_user_cannot_update_other_registration(self, *args):
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {}
        )

        self.other_user = User.objects.get(pk=2)
        AbakusGroup.objects.get(name="Abakus").add_user(self.other_user)
        self.client.force_authenticate(self.other_user)
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.json()["id"]),
            {"feedback": "UPDATED"},
        )
        self.assertEqual(res.status_code, 403)

    def test_admin_update_registration(self, *args):
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {}
        )

        self.webkom_user = User.objects.get(pk=2)
        AbakusGroup.objects.get(name="Webkom").add_user(self.webkom_user)
        self.client.force_authenticate(self.webkom_user)
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.json()["id"]),
            {"feedback": "UPDATED_BY_ADMIN"},
        )
        registration = Registration.objects.get(id=res.json()["id"])
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["feedback"], "UPDATED_BY_ADMIN")
        self.assertEqual(registration.updated_by, self.webkom_user)

    def test_can_not_unregister_other_user(self, *args):
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        registration = Registration.objects.get(user=self.abakus_user, event=event)

        self.other_user = User.objects.get(pk=2)
        AbakusGroup.objects.get(name="Abakus").add_user(self.other_user)
        self.client.force_authenticate(self.other_user)
        registration_response = self.client.delete(
            _get_registrations_detail_url(event.id, registration.id)
        )

        self.assertEqual(registration_response.status_code, 403)

    def test_required_feedback_failing(self, *args):
        """Test that register returns 400 when not providing feedback when required"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        event.feedback_required = True
        event.save()
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {}
        )
        self.assertEqual(registration_response.status_code, 400)

    def test_required_feedback_success(self, *args):
        """Test that register returns 202 when providing feedback when required"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        event.feedback_required = True
        event.save()
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {"feedback": "TEST"}
        )
        self.assertEqual(registration_response.status_code, 202)

    def test_update_payment_status_with_permissions(self, mock_verify_captcha):
        """Test user with permission can update payment_status"""
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {}
        )
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.json()["id"]),
            {"payment_status": "manual"},
        )
        self.assertEqual(res.status_code, 200)

    def test_update_payment_status_wrongly_with_permissions(self, mock_verify_captcha):
        """Test user with permission fails in updating payment_status when giving wrong choice"""
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)

        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {}
        )
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.json()["id"]),
            {"payment_status": "feil-data"},
        )
        self.assertEqual(res.status_code, 400)

    def test_update_payment_status_without_permissions(self, mock_verify_captcha):
        """Test that user without permission cannot update _status"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {}
        )
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.data.json()["id"]),
            {"payment_status": "manual"},
        )
        self.assertEqual(res.status_code, 403)


class EventAdministrateTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_users.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        self.abakus_user = User.objects.get(pk=1)
        self.event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")

    def test_with_group_permission(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(
            f"{_get_detail_url(self.event.id)}administrate/"
        )
        self.assertEqual(event_response.status_code, 200)
        self.assertEqual(event_response.json().get("id"), self.event.id)
        self.assertEqual(len(event_response.json().get("pools")), 2)

    def test_without_group_permission(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(
            f"{_get_detail_url(self.event.id)}administrate/"
        )
        self.assertEqual(event_response.status_code, 403)


class CreateAdminRegistrationTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_users.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        self.abakus_users = User.objects.all()
        self.request_user, self.user = self.abakus_users[0:2]
        self.event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        self.event.start_time = timezone.now() + timedelta(hours=3)
        self.event.save()
        self.pool = self.event.pools.first()

    def test_with_admin_permission(self):
        AbakusGroup.objects.get(name="Webkom").add_user(self.request_user)
        pool_two = self.event.pools.get(name="Webkom")

        self.assertFalse(self.event.can_register(self.user, self.pool))
        self.client.force_authenticate(self.request_user)

        registration_response = self.client.post(
            f"{_get_registrations_list_url(self.event.id)}admin_register/",
            {
                "user": self.user.id,
                "pool": self.pool.id,
                "admin_registration_reason": "test",
            },
        )

        self.assertEqual(registration_response.status_code, 201)
        self.assertEqual(self.pool.registrations.count(), 1)
        self.assertEqual(pool_two.registrations.count(), 0)
        self.assertEqual(
            registration_response.json()["createdBy"], self.request_user.id
        )
        self.assertEqual(
            registration_response.json()["updatedBy"], self.request_user.id
        )

    def test_without_admin_permission(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.user)

        self.assertTrue(self.event.can_register(self.user, self.pool))
        self.client.force_authenticate(self.request_user)

        registration_response = self.client.post(
            f"{_get_registrations_list_url(self.event.id)}admin_register/",
            {
                "user": self.user.id,
                "pool": self.pool.id,
                "admin_registration_reason": "test",
            },
        )

        self.assertEqual(registration_response.status_code, 403)
        self.assertEqual(self.event.number_of_registrations, 0)

    def test_with_nonexistant_pool(self):
        AbakusGroup.objects.get(name="Webkom").add_user(self.request_user)
        AbakusGroup.objects.get(name="Abakus").add_user(self.user)
        nonexistant_pool_id = len(self.event.pools.all())

        self.assertTrue(self.event.can_register(self.user, self.pool))
        self.client.force_authenticate(self.request_user)

        registration_response = self.client.post(
            f"{_get_registrations_list_url(self.event.id)}admin_register/",
            {
                "user": self.user.id,
                "pool": nonexistant_pool_id,
                "admin_registration_reason": "test",
            },
        )

        self.assertEqual(registration_response.status_code, 400)
        self.assertEqual(self.event.number_of_registrations, 0)

    def test_with_feedback(self):
        AbakusGroup.objects.get(name="Webkom").add_user(self.request_user)
        self.client.force_authenticate(self.request_user)
        registration_response = self.client.post(
            f"{_get_registrations_list_url(self.event.id)}admin_register/",
            {
                "user": self.user.id,
                "pool": self.pool.id,
                "feedback": "TEST",
                "admin_registration_reason": "test",
            },
        )

        self.assertEqual(registration_response.status_code, 201)
        self.assertEqual(registration_response.json().get("feedback"), "TEST")
        self.assertEqual(
            registration_response.json()["createdBy"], self.request_user.id
        )
        self.assertEqual(
            registration_response.json()["updatedBy"], self.request_user.id
        )

    def test_without_admin_registration_reason(self):
        AbakusGroup.objects.get(name="Webkom").add_user(self.request_user)
        self.client.force_authenticate(self.request_user)
        registration_response = self.client.post(
            f"{_get_registrations_list_url(self.event.id)}admin_register/",
            {
                "user": self.user.id,
                "pool": self.pool.id,
                "feedback": "TEST",
                "admin_registration_reason": "",
            },
        )

        self.assertEqual(registration_response.status_code, 400)

    def test_ar_to_waiting_list(self):
        AbakusGroup.objects.get(name="Webkom").add_user(self.request_user)
        self.client.force_authenticate(self.request_user)
        self.assertEqual(self.event.waiting_registrations.count(), 0)

        registration_response = self.client.post(
            f"{_get_registrations_list_url(self.event.id)}admin_register/",
            {"user": self.user.id, "admin_registration_reason": "test"},
        )

        self.assertEqual(registration_response.status_code, 201)
        self.assertEqual(self.event.waiting_registrations.count(), 1)


class AdminUnregistrationTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_users.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        self.abakus_users = User.objects.all()
        self.webkom_user = User.objects.first()
        AbakusGroup.objects.get(name="Webkom").add_user(self.webkom_user)
        self.event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        self.event.created_by = self.abakus_users.first()
        self.event.start_time = timezone.now() + timedelta(hours=3)
        self.event.save()

    def test_admin_unregistration(self):
        AbakusGroup.objects.get(name="Webkom").add_user(self.webkom_user)
        user = self.event.registrations.exclude(pool=None).first()

        self.client.force_authenticate(self.webkom_user)
        registrations_before = self.event.number_of_registrations

        registration_response = self.client.post(
            f"{_get_registrations_list_url(self.event.id)}admin_unregister/",
            {"user": user.id, "admin_unregistration_reason": "test"},
        )

        self.assertEqual(registration_response.status_code, 200)
        self.assertEqual(registration_response.json()["updatedBy"], self.webkom_user.id)
        self.assertEqual(self.event.number_of_registrations, registrations_before - 1)

    def test_admin_unregistration_without_permission(self):
        non_admin_user = get_dummy_users(1)[0]
        user = self.event.registrations.exclude(pool=None).first()

        self.client.force_authenticate(non_admin_user)

        registration_response = self.client.post(
            f"{_get_registrations_list_url(self.event.id)}admin_unregister/",
            {"user": user.id, "admin_unregistration_reason": "test"},
        )

        self.assertEqual(registration_response.status_code, 403)

    def test_without_admin_unregistration_reason(self):
        """ Test that admin cannot unregister user without unregistration reason"""
        self.client.force_authenticate(self.webkom_user)
        user = self.event.registrations.exclude(pool=None).first()

        registration_response = self.client.post(
            f"{_get_registrations_list_url(self.event.id)}admin_unregister/",
            {"user": user.id, "admin_unregistration_reason": ""},
        )

        self.assertEqual(registration_response.status_code, 400)


@skipIf(not stripe.api_key, "No API Key set. Set STRIPE_TEST_KEY in ENV to run test.")
class StripePaymentTestCase(BaseAPITestCase):
    """
    Testing cards used:
    https://stripe.com/docs/testing#cards
    """

    fixtures = [
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_users.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        self.abakus_user = User.objects.get(pk=1)
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        self.event = Event.objects.get(title="POOLS_AND_PRICED")

    def issue_payment(self, token):
        return self.client.post(
            _get_detail_url(self.event.id) + "payment/", {"token": token.id}
        )

    def test_payment(self):
        token = create_token("4242424242424242", "123")
        res = self.issue_payment(token)
        self.assertEqual(res.status_code, 202)
        self.assertEqual(res.data.get("payment_status"), constants.PAYMENT_PENDING)
        registration_id = res.json().get("id")
        get_object = self.client.get(
            _get_registrations_detail_url(self.event.id, registration_id)
        )
        self.assertEqual(get_object.json().get("payment_status"), "succeeded")

    def test_refund_task(self):
        token = create_token("4242424242424242", "123")
        self.issue_payment(token)
        registration = Registration.objects.get(event=self.event, user=self.abakus_user)

        stripe.Refund.create(charge=registration.charge_id)

        stripe_events_all = stripe.Event.all(limit=3)
        stripe_event = None
        for obj in stripe_events_all.json():
            if obj.json().object.id == registration.charge_id:
                stripe_event = obj
                break
        self.assertIsNotNone(stripe_event)

        stripe_webhook_event.delay(
            event_id=stripe_event.id, event_type="charge.refunded"
        )

        registration.refresh_from_db()

        self.assertEqual(registration.payment_status, "succeeded")
        self.assertEqual(registration.payment_amount, 10000)
        self.assertEqual(registration.payment_amount_refunded, 10000)

    def test_refund_webhook_raising_error(self):
        token = create_token("4242424242424242", "123")
        self.issue_payment(token)
        registration = Registration.objects.get(event=self.event, user=self.abakus_user)

        stripe.Refund.create(charge=registration.charge_id)

        stripe_events_all = stripe.Event.all(limit=3)
        stripe_event = None
        for obj in stripe_events_all.json():
            if obj.json().object.id == registration.charge_id:
                stripe_event = obj
                break
        self.assertIsNotNone(stripe_event)

        registration.delete()
        with self.assertRaises(WebhookDidNotFindRegistration):
            stripe_webhook_event(event_id=stripe_event.id, event_type="charge.refunded")


class CapacityExpansionTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_events.yaml",
        "test_companies.yaml",
    ]

    def setUp(self):
        self.webkom_user = User.objects.get(pk=1)

        abakus_group = AbakusGroup.objects.get(name="Abakus")
        webkom_group = AbakusGroup.objects.get(name="Webkom")
        webkom_group.add_user(self.webkom_user)
        self.client.force_authenticate(self.webkom_user)
        event_data = _test_event_data[0]
        event_data["pools"][0]["permissionGroups"] = [abakus_group.id]

        self.event_response = self.client.post(_get_list_url(), event_data)
        self.event = Event.objects.get(id=self.event_response.json().pop("id", None))
        self.event.start_time = timezone.now() + timedelta(hours=3)
        users = get_dummy_users(11)
        for user in users:
            abakus_group.add_user(user)
            registration = Registration.objects.get_or_create(
                event=self.event, user=user
            )[0]
            self.event.register(registration)
        self.assertEquals(self.event.waiting_registrations.count(), 1)
        self.updated_event = deepcopy(event_data)
        self.updated_event["pools"][0]["id"] = self.event_response.json()["pools"][0][
            "id"
        ]

    def test_bump_on_pool_expansion(self):
        self.updated_event["pools"][0]["capacity"] = 11
        response = self.client.put(_get_detail_url(self.event.id), self.updated_event)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.event.waiting_registrations.count(), 0)

    def test_bump_on_pool_creation(self):
        self.updated_event["pools"].append(_test_pools_data[0])
        response = self.client.put(_get_detail_url(self.event.id), self.updated_event)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.event.waiting_registrations.count(), 0)

    def test_no_bump_on_reduced_pool_size(self):
        self.updated_event["pools"][0]["capacity"] = 9
        response = self.client.put(_get_detail_url(self.event.id), self.updated_event)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.event.waiting_registrations.count(), 1)


class RegistrationSearchTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_events.yaml",
        "test_companies.yaml",
    ]

    def setUp(self):
        self.webkom_user = User.objects.get(pk=1)

        abakus_group = AbakusGroup.objects.get(name="Abakus")
        webkom_group = AbakusGroup.objects.get(name="Webkom")
        webkom_group.add_user(self.webkom_user)
        self.client.force_authenticate(self.webkom_user)
        event_data = _test_event_data[0]
        event_data["pools"][0]["permissionGroups"] = [abakus_group.id]

        self.event_response = self.client.post(_get_list_url(), event_data)
        self.event = Event.objects.get(id=self.event_response.json().pop("id", None))
        self.event.start_time = timezone.now() + timedelta(hours=3)
        self.users = get_dummy_users(11)
        for user in self.users:
            abakus_group.add_user(user)
            registration = Registration.objects.get_or_create(
                event=self.event, user=user
            )[0]
            self.event.register(registration)

    def test_register_presence(self):
        self.client.force_authenticate(self.webkom_user)
        res = self.client.post(
            _get_registration_search_url(self.event.pk),
            {"username": self.users[0].username},
        )
        self.assertEquals(res.status_code, 200)
        self.assertNotEqual(res.json().get("user", None), None)

    def test_asd_user(self):
        self.client.force_authenticate(self.webkom_user)
        res = self.client.post(
            _get_registration_search_url(self.event.pk),
            {"username": "asd007 xXx james bond"},
        )
        self.assertEquals(res.status_code, 400)

    def test_no_username(self):
        self.client.force_authenticate(self.webkom_user)
        res = self.client.post(_get_registration_search_url(self.event.pk), {})
        self.assertEquals(res.status_code, 400)

    def test_user_not_registered(self):
        self.client.force_authenticate(self.webkom_user)
        res = self.client.post(
            _get_registration_search_url(self.event.pk),
            {"username": self.webkom_user.username},
        )
        self.assertEquals(res.status_code, 400)

    def test_auth(self):
        self.client.force_authenticate(self.users[0])
        res = self.client.post(
            _get_registration_search_url(self.event.pk),
            {"username": self.users[0].username},
        )
        self.assertEquals(res.status_code, 403)

    def test_double_register(self):
        self.client.force_authenticate(self.webkom_user)
        res = self.client.post(
            _get_registration_search_url(self.event.pk),
            {"username": self.users[0].username},
        )
        res = self.client.post(
            _get_registration_search_url(self.event.pk),
            {"username": self.users[0].username},
        )
        self.assertEquals(res.status_code, 400)


class UpcomingEventsTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_users.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        date = timezone.now().replace(hour=16, minute=15, second=0, microsecond=0)
        for event in Event.objects.all():
            event.start_time = date + timedelta(days=10)
            event.end_time = date + timedelta(days=10, hours=4)
            event.save()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_upcoming_url())
        self.assertEqual(event_response.status_code, 200)
        self.assertEqual(len(event_response.json()), 2)

    def test_filter_out_old(self):
        event = Event.objects.filter(registrations__user=self.abakus_user).first()
        event.start_time = timezone.now() - timedelta(days=10)
        event.end_time = timezone.now() - timedelta(days=10)
        event.save()

        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_upcoming_url())
        self.assertEqual(event_response.status_code, 200)
        self.assertEqual(len(event_response.json()), 1)
        self.assertNotEqual(event_response.json()[0]["id"], event.pk)

    def test_unauthenticated(self):
        event_response = self.client.get(_get_upcoming_url())
        self.assertEqual(event_response.status_code, 401)
