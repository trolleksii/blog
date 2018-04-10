from rest_framework import status
from rest_framework.views import exception_handler


def core_exception_handler(exc, context):
    exception_class = exc.__class__.__name__
    if exception_class in ['AuthenticationFailed', 'NotAuthenticated']:
        setattr(exc, 'auth_header', 'Bearer realm="Blog"')
        setattr(exc, 'status_code', status.HTTP_401_UNAUTHORIZED)
    response = exception_handler(exc, context)
    handlers = {
        'Http404': _handle_not_found_error,
        'ValidationError': _handle_validation_error
    }
    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    return _handle_generic_error(exc, context, response)


def _handle_generic_error(exc, context, response):
    exc_code = exc.get_codes()
    response.data = {
        'errors': {
            exc_code: [response.data['detail']]
        }
    }
    return response


def _handle_validation_error(exc, context, response):
    response.data = {
        'errors': response.data
    }
    return response


def _handle_not_found_error(exc, context, response):
    # retrieve model name of requested object
    model_name = context['view'].serializer_class.Meta.model._meta.verbose_name
    response.data = {
        'errors': {
            model_name: [response.data['detail']]
        }
    }
    return response
