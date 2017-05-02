import re

from coupon import error


def is_tel(s):
    return bool(re.fullmatch(r'^1[34578]\d{9}$', s))


def check_tel(s):
    if not is_tel(s):
        raise error.ValidationError('tel')
