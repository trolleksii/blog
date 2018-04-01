from rest_framework.views import exception_handler


def core_exception_handler(exc, context):
    response = exception_handler(exc, context)
    handlers = {
        'NotFound': _handle_not_found_error,
        'ValidationError': _handle_generic_error,
        'AuthenticationFailed': _handle_auth_token_error,
        'NotAuthenticated': _handle_generic_error,
        'Http404': _handle_not_found_error
    }
    exception_class = exc.__class__.__name__
    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    return response


def _handle_generic_error(exc, context, response):
    response.data = {
        'errors': response.data
    }
    return response


def _handle_not_found_error(exc, context, response):
    response.data = {
        'errors': response.data
    }
    return response


def _handle_auth_token_error(exc, context, response):
    response.data = {
        'errors': {
            'token': response.data['detail']
        }
    }
    return response
