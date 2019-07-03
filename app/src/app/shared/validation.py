import base64
import re

from app.shared.utils import convert_timestamp


def validate_hash(value):
    if not value or not re.match(r'^[0-9a-fA-F]{64}$', str(value)):
        return False

    return True


def validate_uuid(value):
    if not value or not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', str(value)):
        return False

    return True


def validate_url(value):
    if not re.match(r'^https?:\/\/([a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,}|[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})(:[0-9]{1,5})?(\/.*)?$', value.lower()):
        return False

    return True


def validate_device_token(value):
    return True


def validate_base64(value):
    try:
        return base64.b64encode(base64.b64decode(value)) == value
    except Exception:
        return False


def validate_timestamp(value):
    if not convert_timestamp(value):
        return False

    return True
