import string
import random

from django.db.models import Model
from django.utils.text import slugify


def _generate_suffix(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slugify(*, model=None, text=''):
    """
    Returns unique slug for a given model, from given text by appending unique
    prefix.
    """
    assert issubclass(model, Model)
    assert text != ''
    assert isinstance(text, str)
    slug_exists = True
    while slug_exists:
        slug = '{}-{}'.format(slugify(text), _generate_suffix())
        slug_exists = model._default_manager.filter(slug=slug).exists()
    return slug
