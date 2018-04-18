from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.views import exception_handler

from apps.authentication.backends import JWTAuthentication


def core_exception_handler(exc, context):
    exception_class = exc.__class__.__name__
    if exception_class in ['AuthenticationFailed', 'NotAuthenticated']:
        setattr(exc, 'auth_header', JWTAuthentication.keyword)
        setattr(exc, 'status_code', HTTP_401_UNAUTHORIZED)
    response = exception_handler(exc, context)
    detail = response.data.pop('detail', None)
    if detail:
        error_code = exc.get_codes()
        response.data[error_code] = detail
    return _wrap_error_response(response)


def _wrap_error_response(response):
    response.data = {
        'errors': response.data
    }
    return response
