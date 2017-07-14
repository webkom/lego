class BaseHandler:

    def __init__(self):
        pass

    def handle_event(self, instance, event):
        '''
        Receives an event on an instance and sends a corresponding activity into feeds
        :param instance: instance of object
        :param event: type of event. For example 'create' or 'update'
        :return: None
        '''

        if event == 'create':
            self.handle_create(instance)
        elif event == 'update':
            self.handle_update(instance)
        elif event == 'delete':
            self.handle_delete(instance)
        else:
            handler = getattr(self, f'handle_{event}', None)
            if handler:
                handler(instance)

    def handle_create(self, instance):
        pass

    def handle_update(self, instance):
        pass

    def handle_delete(self, instance):
        pass
