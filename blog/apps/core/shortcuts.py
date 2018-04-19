from rest_framework.exceptions import NotFound


def get_object_or_404(model, **kwargs):
    """
    Query db for a single object of <model> by one or more search criteria. 

    For example:

    get_object_or_404(User, first_name='John', last_name='Smith').

    Will raise rest_framework.exceptions.NotFound if query fails.
    """
    try:
        obj = model._default_manager.get(**kwargs)
        return obj
    except model.DoesNotExist:
        model_name = model._meta.verbose_name.capitalize()
        raise NotFound('{} not found.'.format(model_name))
