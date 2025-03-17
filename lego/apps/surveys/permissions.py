from django.db.models import Q

from lego.apps.events.constants import PRESENCE_CHOICES
from lego.apps.permissions.constants import CREATE, EDIT, VIEW
from lego.apps.permissions.permissions import PermissionHandler


class SurveyPermissionHandler(PermissionHandler):
    default_require_auth = True

    def filter_queryset(self, user, queryset, **kwargs):
        if not user or not user.is_authenticated:
            return queryset.none()

        is_survey_admin = super().has_perm(
            user,
            EDIT,
            queryset=queryset,
            check_keyword_permissions=True,
        )
        if is_survey_admin:
            return queryset.all()

        return queryset.filter(
            Q(event__registrations__user=user)
            & Q(event__registrations__presence=PRESENCE_CHOICES.PRESENT)
        ).distinct()

    def has_perm(
        self,
        user,
        perm,
        request=None,
        view=None,
        obj=None,
        queryset=None,
        check_keyword_permissions=True,
        **kwargs,
    ):
        if obj is None and queryset is None:
            return False

        user_attended_event = False
        survey_pk = None
        survey = None
        is_survey_admin = super().has_perm(
            user,
            EDIT,
            obj=obj,
            queryset=queryset,
            check_keyword_permissions=True,
        )

        if view is not None:
            if view.action in ["share", "hide", "csv", "pdf"]:
                return is_survey_admin

            survey_pk = view.kwargs.get("pk", None)
            if survey_pk:
                try:
                    survey = queryset.get(id=survey_pk)
                except queryset.model.DoesNotExist:
                    survey = None
            if survey and user:
                user_attended_event = survey.event.registrations.filter(
                    user=user.id, presence=PRESENCE_CHOICES.PRESENT
                ).exists()

        if perm is CREATE:
            return is_survey_admin

        if perm is VIEW:
            if request and request.auth and isinstance(request.auth, survey.__class__):
                """
                Allow permission when token matches survey
                """
                return int(request.auth.id) == int(survey_pk)

            return user_attended_event or is_survey_admin

        return super().has_perm(
            user, perm, obj, queryset, check_keyword_permissions, **kwargs
        )


class SubmissionPermissionHandler(PermissionHandler):
    default_require_auth = True

    def filter_queryset(self, user, queryset, **kwargs):
        if not user.is_authenticated:
            return queryset.none()

        if self.has_perm(user, EDIT, queryset=queryset):
            return queryset

        return queryset.filter(user=user)

    def has_perm(
        self,
        user,
        perm,
        obj=None,
        queryset=None,
        view=None,
        request=None,
        check_keyword_permissions=True,
        **kwargs,
    ):
        if not user or not user.is_authenticated:
            return False

        from lego.apps.surveys.models import Survey

        user_attended_event = False
        is_survey_admin = user.has_perm(EDIT, obj=Survey)
        has_perm = super().has_perm(
            user, perm, obj, queryset, check_keyword_permissions, **kwargs
        )

        if view is not None:
            if view.action in ["update", "partial_update"]:
                return False

            if view.action in ["hide", "show"]:
                return is_survey_admin

            survey_pk = view.kwargs["survey_pk"]
            survey = Survey.objects.get(id=survey_pk)
            user_attended_event = survey.event.registrations.filter(
                user=user.id, presence=PRESENCE_CHOICES.PRESENT
            ).exists()

        if is_survey_admin:
            return True

        if perm is VIEW:
            if obj:
                return user_attended_event and obj.user == user
            if queryset:
                return all(submission.user == user for submission in queryset)

        if request is not None:
            query_user = request.query_params.get("user", False)
            if query_user:
                return user_attended_event and int(query_user) is int(user.id)

        if perm is CREATE:
            return has_perm and user_attended_event

        return has_perm
