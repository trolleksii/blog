import jwt

from datetime import datetime, timedelta

from django.contrib.auth.models import AbstractUser

from blog.settings import SECRET_KEY


class User(AbstractUser):
    """
    User with JWT.
    Token validity time is 24 hours by default. You can specify custom time in
    hours by adding parameter `token_valid_for` on initialization of class object.
    """
    JWT_VALIDITY_IN_HOURS = 24

    def __init__(self, *args, **kwargs):
        jwt_validity_period = kwargs.pop('token_valid_for', self.JWT_VALIDITY_IN_HOURS)
        super(User, self).__init__(*args, **kwargs)
        setattr(self, '_token_valid_for', jwt_validity_period)

    @property
    def token(self):
        return self._generate_jwt()

    def _generate_jwt(self):
        validity_period = timedelta(hours=self._token_valid_for)
        token = jwt.encode(
            {
                'id': self.pk,
                'exp': datetime.timestamp(datetime.now() + validity_period),
            },
            SECRET_KEY,
            algorithm='HS256',
        )
        return token.decode('utf-8')
