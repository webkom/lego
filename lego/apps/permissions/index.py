from structlog import get_logger

log = get_logger()


class PermissionIndex:
    """
    Base class for permission indexes. Implement this class to index a model. Remember to use the
    register function to register the index.
    """

    queryset = None
    list = None
    retrieve = None
    create = None
    update = None
    partial_update = None
    destroy = None

    def get_queryset(self):
        """
        Get the queryset that should be indexed. Override this method or set a queryset attribute
        on this class.
        """
        queryset = getattr(self, 'queryset')

        if queryset is None:
            raise NotImplementedError(
                f'You must provide a \'get_qyeryset\' method or queryset attribute for the {self} '
                f'index.'
            )
        return queryset

    def get_model(self):
        """
        Get the model this index is bound to.
        """
        queryset = self.get_queryset()
        return queryset.model

    def check_can_register(self):
        pass
