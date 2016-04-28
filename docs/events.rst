Events
======

Flow for (un)registration
-------------------------

Upon registration
*****************

In the ``RegistrationCreateAndUpdateSerializer`` we pull the current user from the validated data,
and the event from the view, through ``self.context['view'].kwargs['event_pk']``.
The user is sent as the argument to ``event.register(user)``.

In the register-method we try to find the optimal pool for the user, if he's able to
register for the event. There are three possible outcomes:

1) The user does not have permission to join any pools, and an exception is raised.
2) The user is added to the waiting list, along with any pools he is able to join.
3) The user is added to a pool, and the registration is successful.

First we iterate over all the pools in the event to build a list of pools the user is able to join.
If the list is empty, the user is not allowed to register for the event, and we raise an exception.
If the event only has one pool, and the user is able to join it, we can simply check if the pool
is full and register the user accordingly. If it's full a Registration is created, with no pool, and
the list of possible pools as ``waiting_pools``. If it's not full a Registration is created, with the
only pool as the ``pool``.

If the event is merged, the situation is similar: we simply check if the event is full, and register
the user accordingly. The user is put in the first possible pool, since pools don't matter post-merge.

If the event isn't merged we build a list of full pools by popping full pools from the list of
possible pools. This is done in a helper-method. There are three possible outcomes:

1) The list of possible pools is empty.
    - All available pools are full, and from the POV of the user the event is full.
    - The user is registered in the waiting list.
    - The list of full pools is used as the list of pools that the user is waiting for.
2) There is only one possible pool left.
    - The user is registered for this pool.
3) There are several pools left
    - The search continues...

The "algorithm" now builds a dictionary where `key=pool` and `value=total users who can join the pool`,
because we are trying to find the most exclusive pool. If there are several pools with the same
exclusivity, the one with the highest capacitiy is chosen. This is done through 3 helper-methods,
and the user is now registered.

Upon unregistration
*******************

In the unregistration-method the registration belonging to the user is acquired, it's current pool
is stored in a temporary variable, and the fields ``pool``, ``waiting_list`` and ``waiting_pool``
are cleared. The unregistration date is set, and it is saved.

Then we call ``check_for_bump(pool)``, where `pool = the temporary pool from earlier`.
Here we check if there's room for a bump, and if so we call the bump-method. The `from_pool`-argument
is the pool we unregistered from earlier. If the event is merged, we ignore the pool.

In `bump` we pop the first person in the waiting list. If `from_pool` is not None, the first person who
can join that pool is popped. This registration has it's ``waiting_list``, ``waiting_pool`` and
``unregistration_date`` cleared, and it's pool set to either `from_pool`
or the first pool that the user can join.


Models
------
.. automodule:: lego.app.events.models
    :members:
    :show-inheritance:
