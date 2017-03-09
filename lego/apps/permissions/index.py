from structlog import get_logger

log = get_logger()


class PermissionIndex:
    """
    Base class for permission indexes. Implement this class to index a model. Remember to use the
    register function to register the index.
    """

    model = None

    list = None
    retrieve = None
    create = None
    update = None
    partial_update = None
    destroy = None

    safe_methods = ['list', 'retrieve']
