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
        Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9....
    """

    keyword = 'Token'
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
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)
        token = auth[1]
        try:
            payload = jwt.decode(token, secret, algorithms=self.ALGORITHMS)
        except Exception as e:
            raise exceptions.AuthenticationFailed(e)
        return self.authenticate_credentials(payload['id'])

    def authenticate_credentials(self, pk):
        """
        Returns user and token if a user with such pk exists and active.
        """
        try:
            user = User.objects.get(pk=pk)
        except ObjectDoesNotExist:
            msg = _('No user matching this token was found.')
            raise exceptions.AuthenticationFailed(msg)
        if not user.is_active:
            msg = _('This user has been deactivated.')
            raise exceptions.AuthenticationFailed(msg)
        return (user, user.token)
