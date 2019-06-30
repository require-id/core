import datetime
import re


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
