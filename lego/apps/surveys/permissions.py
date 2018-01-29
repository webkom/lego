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
                event=event.id, user=user.id, presence=constants.PRESENT).exists()

            return user_attended_event
        return False


class SubmissionPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        from lego.apps.surveys.models import Survey
        survey = Survey.objects.get(id=view.kwargs['survey_pk'])
        event = getattr(survey, 'event')
        user = request.user
        user_attended_event = Registration.objects.filter(
            event=event.id, user=user.id, presence=constants.PRESENT).exists()

        if user.has_perm(EDIT, obj=Survey):
            return True
        if view.action in ['create']:
            return user_attended_event
        elif view.action in ['retrieve']:
            return user_attended_event and \
                   survey.submissions.get(id=view.kwargs['pk']).user_id is user.id
        return False
