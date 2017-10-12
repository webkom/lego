from lego.apps.permissions.constants import CREATE, LIST
from lego.apps.permissions.permissions import PermissionHandler
from lego.apps.permissions.utils import get_permission_handler


class CompanyPermissionHandler(PermissionHandler):

    default_keyword_permission = '/sudo/admin/companies/{perm}/'


class NestedCompanyPermissionHandler(CompanyPermissionHandler):
    """
    Lookup permissions on the parent company object.
    """

    def has_perm(
            self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):
        from lego.apps.companies.models import Company
        if obj is not None:
            obj = obj.company

        company_permission_handler = get_permission_handler(Company)
        has_perm = company_permission_handler.has_perm(
            user, perm, obj=obj, queryset=Company.objects.none()
        )

        return has_perm


class SemesterPermissionHandler(PermissionHandler):

    default_keyword_permission = '/sudo/admin/companies/{perm}/'

    authentication_map = {
        LIST: False,
    }


class CompanyContactPermissionHandler(NestedCompanyPermissionHandler):
    """
    Lookup permissions on the parent company object and allow public view based on the public
    property.
    """

    def filter_queryset(self, user, queryset, **kwargs):
        return queryset.filter(public=True)


class CompanyInterestPermissionHandler(PermissionHandler):
    """
    Allow creation of CompanyInterest without a valid user.
    """
    default_keyword_permission = '/sudo/admin/companyinterest/{perm}'

    authentication_map = {
        CREATE: False,
    }
