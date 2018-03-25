import jwt

from datetime import datetime, timedelta

from django.contrib.auth.models import AbstractUser

from blog.settings import SECRET_KEY


class User(AbstractUser):
    """
    User with JWT.
    Token validity time is 24 hours by default. You can specify custom time in
    hours by:
        1. Adding parameter `token_valid_for` on initialization of class object
        2. Adding parameter `TOKEN_VALID_FOR` to the project config file
    """

    def __init__(self, *args, **kwargs):
        token_valid_for = kwargs.pop('token_valid_for', 24)
        super(User, self).__init__(*args, **kwargs)
        try:
            from blog.settings import TOKEN_VALID_FOR
            token_valid_for = int(TOKEN_VALID_FOR)
        except ImportError:
            # not configured
            pass
        except ValueError:
            # parameter is no convertable to int
            pass
        setattr(self, 'token_valid_for', token_valid_for)

    @property
    def token(self):
        return self._generate_jwt()

    def _generate_jwt(self):
        validity_period = timedelta(hours=self.token_valid_for)
        token = jwt.encode(
            {
                'id': self.pk,
                'exp': datetime.timestamp(datetime.now() + validity_period),
            },
            SECRET_KEY,
            algorithm='HS256',
        )
        return token.decode('utf-8')
