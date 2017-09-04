class PublicObjectPermissionsManagerMixin:
    """
    Use this mixin in a manager if you need a manager that returns public objects only.
    """

    def get_queryset(self):
        return super().get_queryset().filter(require_auth=False)
