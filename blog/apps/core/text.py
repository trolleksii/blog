import string
import random

from django.utils.text import slugify


def _generate_suffix(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slugify(text):
    slug = slugify(text)
    suffix = _generate_suffix()
    return '-'.join([slug, suffix])
