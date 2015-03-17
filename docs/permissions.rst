Permissions
===========

Model Permissions
-----------------

Model permissions are only assigned to Django's Group model, and thus these work as permission
categories. This means we will have groups similar to these:

- EventAdmin, which could contain the permissions "add_event", "delete_event" and "change_event".
- EventCreator, which would only contain "add_event".

Our group model, AbakusGroup, will have a connection to the permission
groups its members have access to. Permission groups will never be connected directly to a user,
to make it simpler to maintain.

The permission group abstraction is done to simplify how permissions are maintained, and to
avoid having to deal with Django permissions directly from the frontend/admin panel.

Object Permissions
------------------

Object permissions are handled explicitly by each app themself. This is done by inheriting the
abstract model ObjectPermissionsModel, which adds the fields ``can_view_groups``,
``can_edit_groups`` and ``can_edit_users``. These are then used by mixins like
lego.permissions.ObjectPermissions to decide if a user has permission to access an event/article
or similar.

Modules
-------

Filters
-------
.. automodule:: lego.permissions.filters
    :members:
    :show-inheritance:

Models
------
.. automodule:: lego.permissions.models
    :members:
    :show-inheritance:


Permission Classes
------------------
.. automodule:: lego.permissions.object_permissions
    :members:
    :show-inheritance:
