import datetime
import hashlib
import re
from typing import Awaitable


def convert_timestamp(timestamp):
    datetime_object = None

    for fmt in (
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y-%m-%dT%H:%M:%S.%f UTC',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S UTC',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%fZ',
        '%Y-%m-%d %H:%M:%S.%f UTC',
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%d %H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S UTC',
        '%Y-%m-%d %H:%M:%S'
    ):
        try:
            datetime_object = datetime.datetime.strptime(timestamp, fmt)
            break
        except ValueError:
            pass

    return datetime_object


def snake_case(key):
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', key)

    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def camel_case(key):
    acronyms = ['api']
    key = key.lower()

    return ''.join([key.split('_')[0]] + [w.upper() if w in acronyms else w.capitalize() for w in key.split('_')][1:])


def sha3(value):
    if isinstance(value, str):
        value = value.encode('utf-8')

    return hashlib.sha3_256(value).hexdigest()


def is_expired(value):
    if isinstance(value, str):
        ts = convert_timestamp(value)
    else:
        ts = value

    if ts < datetime.datetime.now():
        return True

    return False


async def async_call(func):
    if isinstance(func, Awaitable):
        return await func

    return func
