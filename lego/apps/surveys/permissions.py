from rest_framework import permissions

from lego.apps.events import constants
from lego.apps.events.models import Registration
from lego.apps.permissions.constants import EDIT


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

            received_token = request.GET.get('token')

            return user_attended_event or (survey.token and received_token == survey.token)
        return False


class SurveyTemplatePermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        from lego.apps.surveys.models import Survey
        user = request.user
        return bool(user.has_perm(EDIT, obj=Survey))


class SubmissionPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        from lego.apps.surveys.models import Survey
        survey = Survey.objects.get(id=view.kwargs['survey_pk'])
        event = getattr(survey, 'event')
        user = request.user
        user_attended_event = Registration.objects.filter(
            event=event.id, user=user.id, presence=constants.PRESENT
        ).exists()
        print('survey perms')

        if view.action in ['update', 'partial_update']:
            return False
        if user.has_perm(EDIT, obj=Survey):
            return True
        if view.action in ['create']:
            return user_attended_event
        if view.action in ['list']:
            received_token = request.GET.get('token')
            return survey.token and received_token == survey.token
        elif view.action in ['retrieve']:
            return user_attended_event and\
                   survey.submissions.get(id=view.kwargs['pk']).user_id is user.id
        if request.query_params.get('user', False):
            return user_attended_event and int(request.query_params.get('user', False)) is \
                   int(user.id)
        return False
