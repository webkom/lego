from rest_framework import permissions

from lego.apps.events import constants
from lego.apps.events.models import Registration
from lego.apps.permissions.constants import EDIT
from lego.apps.permissions.permissions import PermissionHandler


class SurveyPermissionHandler(PermissionHandler):
    default_keyword_permission = '/sudo/admin/surveys/{perm}/'


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
