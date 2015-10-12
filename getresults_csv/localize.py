import pytz

from django.conf import settings
from django.utils.timezone import make_aware, make_naive

tz = pytz.timezone(settings.TIME_ZONE)


def localize(value):

    def my_make_naive(value, tz):
        try:
            value = make_naive(value, tz)
        except ValueError:
            pass
        return value

    def my_make_aware(value, tz):
        try:
            value = make_aware(value, tz)
        except ValueError:
            pass
        return value

    if settings.USE_TZ:
        value = my_make_aware(value, tz)
    else:
        value = my_make_naive(value, tz)
    return value
