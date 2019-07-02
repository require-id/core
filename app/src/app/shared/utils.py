import base64
import datetime
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


def validate_hash(value):
    if len(value) != 64:
        return False
    if re.match(value, r'^[0-9a-f]{64}$'):
        return False

    return True


def validate_uuid(value):
    if re.match(value, r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'):
        return False

    return True


def validate_validation_code(value):
    if len(value) <= 2:
        return False
    if len(value) >= 7:
        return False
    if re.match(value, r'^[0-9a-zA-Z-]{2,7}$'):
        return False

    return True


def validate_url(value):
    if not re.match(r'^(http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,}(:[0-9]{1,5})?(\/.*)?$', value.lower()):
        return False

    return True


def validate_device_token(value):
    return True


def validate_base64(value):
    try:
        return base64.b64encode(base64.b64decode(value)) == value
    except Exception:
        return False


def get_query_value(event, keys, default=None):
    if isinstance(keys, str):
        keys = (keys, )

    query = event.get('queryStringParameters', {})

    if not query:
        return default

    for key in keys:
        if str(query.get(key, '')):
            return str(query.get(key, ''))

    return default


def get_payload_value(payload, keys, default=None):
    if isinstance(keys, str):
        keys = (keys, )

    for key in keys:
        if str(payload.get(key, '')):
            return str(payload.get(key, ''))

    return default


def sha3(value):
    return hashlib.sha3_256(value).hexdigest()


async def async_call(func):
    if isinstance(func, Awaitable):
        return await func

    return func
