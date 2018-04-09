from rest_framework import status
from rest_framework.views import exception_handler


def core_exception_handler(exc, context):
    response = exception_handler(exc, context)

    handlers = {
        'AuthenticationFailed': _handle_auth_error,
        'Http404': _handle_not_found_error,
        'NotAuthenticated': _handle_auth_error,
        'ValidationError': _handle_validation_error
    }
    exception_class = exc.__class__.__name__
    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    return _handle_generic_error(exc, context, response)


def _handle_auth_error(exc, context, response):
    response.status_code = status.HTTP_401_UNAUTHORIZED
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
