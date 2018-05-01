from rest_framework import permissions

from lego.apps.events import constants
from lego.apps.events.models import Registration
from lego.apps.permissions.constants import EDIT
from lego.apps.surveys.models import Survey


class SurveyPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        from lego.apps.surveys.models import Survey
        user = request.user

        if user.has_perm(EDIT, obj=Survey):
            return True
        elif view.action in ['retrieve']:
            survey = Survey.objects.get(id=view.kwargs['pk'])
            event = getattr(survey, 'event')
            user_attended_event = Registration.objects.filter(
                event=event.id, user=user.id, presence=constants.PRESENT
            ).exists()

            return user_attended_event
        return False


class SubmissionPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        from lego.apps.surveys.models import Survey
        survey = Survey.objects.get(id=view.kwargs['survey_pk'])
        event = getattr(survey, 'event')
        user = request.user
        user_attended_event = Registration.objects.filter(
            event=event.id, user=user.id, presence=constants.PRESENT
        ).exists()

        if view.action in ['update', 'partial_update']:
            return False
        if user.has_perm(EDIT, obj=Survey):
            return True
        if view.action in ['create']:
            return user_attended_event
        elif view.action in ['retrieve']:
            return user_attended_event and\
                   survey.submissions.get(id=view.kwargs['pk']).user_id is user.id
        if request.query_params.get('user', False):
            return user_attended_event and int(request.query_params.get('user', False)) is \
                   int(user.id)
        return False


class SurveyTokenPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action not in ['retrieve']:
            return False
        survey = Survey.objects.get(id=view.kwargs['pk'])
        return request.auth and survey.id is request.auth.id
