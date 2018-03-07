class Handler:
    """
    The handler is responsible for running special events based on an instance.
    Typical use-cases: Feed updates, email and push notifications.

    Implement the handle_{action} function in order to execute code.

    Default actions: create, update, delete
    """

    model = None

    def run(self, instance, action, **kwargs):
        func = getattr(self, f'handle_{action}', None)
        if func:
            return func(instance, **kwargs)

        raise ValueError('Action handler called with nn invalid action')

    def handle_create(self, instance, **kwargs):
        pass

    def handle_update(self, instance, **kwargs):
        pass

    def handle_delete(self, instance, **kwargs):
        pass
