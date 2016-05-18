from .registry import get_model_index


class SignalHandler:
    """
    This handler indexes model changes using async celery tasks.
    """

    def on_save(self, model, instance, created, update_fields):
        model_index = get_model_index(model)
        if model_index:
            model_index.update_instance(instance)

    def on_delete(self, model, instance):
        model_index = get_model_index(model)
        if model_index:
            model_index.remove_instance(instance)
