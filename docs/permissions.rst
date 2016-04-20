Permissions
===========

Model Permissions
-----------------

Lego's permission strings form a hierarchy, where each step is described with a forward slash.
A user with the permission ``/sudo/admin/events/`` will also implicitly have access to
everything that requires the permission ``/sudo/admin/events/create/``, while he or she won't
have access to anything that requires i.e. ``/sudo/admin/users/``.

Example:

Needed permission: ``/sudo/admin/events/create/``

- Permission                    - Passed?

- ``/sudo/admin/users/create/`` - Yes

- ``/sudo/admin/users/update/`` - No

- ``/sudo/admin/``              - Yes


The permission strings can only contain letters and forward slashes, and need to start and end
with a forward slash.

Permissions are stored per group, connected to the model `:class:lego.users.models.AbakusGroup`.
The current permission strings are:
``/sudo/`` - for Webkom
``/sudo/admin/`` for Hovedstyret

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
