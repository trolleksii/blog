import jwt

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
    "Authorization" HTTP header, prepended with the "Bearer " keyword.
    For example:
        Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9....
    """

    keyword = 'Bearer'
    exc_name = 'token_error'
    ALGORITHMS = ['HS256', ]

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth_header = get_authorization_header(request).split()
        token = self._extract_token(auth_header)
        if not token:
            return None
        try:
            payload = jwt.decode(token, secret, algorithms=self.ALGORITHMS)
        except jwt.exceptions.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(e, self.exc_name)
        return self.authenticate_credentials(payload['id'])

    def authenticate_credentials(self, pk):
        """
        Returns user and token if a user with such pk exists and active.
        """
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            msg = _('No user matching this token was found.')
            raise exceptions.AuthenticationFailed(msg, self.exc_name)

        if not user.is_active:
            msg = _('This user has been deactivated.')
            raise exceptions.AuthenticationFailed(msg, self.exc_name)
        return (user, user.token)

    def _extract_token(self, auth_header):
        """
        Extracts token from Authentication header.

        Returns None in case if:
          1. header was not found
          2. keyword is incorrect
          3. header contains more or less than 2 'words'(keyword + token)
        """
        if not auth_header or auth_header[0].lower().decode() != self.keyword.lower():
            return None
        if len(auth_header) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg, self.exc_name)
        elif len(auth_header) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg, self.exc_name)
        return auth_header[1]
