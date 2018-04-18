from rest_framework.exceptions import NotFound


def get_object_or_404(model, **kwargs):
    try:
        obj = model._default_manager.get(**kwargs)
        return obj
    except model.DoesNotExist:
        model_name = model._meta.verbose_name.capitalize()
        raise NotFound('{} not found.'.format(model_name))
