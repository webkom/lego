def has_permission(content_type, object_id, user):
    """
    This function returns true if the user has access to the specified object.
    The permission system is not optimized for these queries. We need to decide how we should do
    this with our system.

    Problems:

    * Models with object permission can be retrieved using the same way the filtering does,
    but this needs to be done for every content_type.

    * Keyword permissions requires a permission string, how should we retrieve this?
    """
    return True
