import jwt

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header, exceptions
)

from blog.settings import SECRET_KEY as secret
from .models import User


class JWTAuthentication(BaseAuthentication):
    """
    Simple JWT based authentication.

    Clients should authenticate by passing the JWT token key in the
    "Authorization" HTTP header, prepended with the string "Token ".
    For example:
        Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9....
    """

    keyword = 'Bearer'
    exc_name = 'jwt_error'
    ALGORITHMS = ['HS256', ]

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower().decode() != self.keyword.lower():
            return None
        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            exc = exceptions.AuthenticationFailed(msg, self.exc_name)
            setattr(exc, 'auth_header', 'Bearer relm="blog"')
            raise exc
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            exc = exceptions.AuthenticationFailed(msg, self.exc_name)
            setattr(exc, 'auth_header', 'Bearer relm="blog"')
            raise exc
        token = auth[1]
        try:
            payload = jwt.decode(token, secret, algorithms=self.ALGORITHMS)
        except Exception as e:
            exc = exceptions.AuthenticationFailed(e, self.exc_name)
            setattr(exc, 'auth_header', 'Bearer relm="blog"')
            raise exc
        return self.authenticate_credentials(payload['id'])

    def authenticate_credentials(self, pk):
        """
        Returns user and token if a user with such pk exists and active.
        """
        try:
            user = User.objects.get(pk=pk)
        except ObjectDoesNotExist:
            msg = _('No user matching this token was found.')
            exc = exceptions.AuthenticationFailed(msg, self.exc_name)
            setattr(exc, 'auth_header', 'Bearer relm="blog"')
            raise exc

        if not user.is_active:
            msg = _('This user has been deactivated.')
            exc = exceptions.AuthenticationFailed(msg, self.exc_name)
            setattr(exc, 'auth_header', 'Bearer relm="blog"')
            raise exc
            return (user, user.token)
