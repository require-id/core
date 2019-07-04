import datetime
import json
import uuid

from app.shared.utils import async_call, camel_case, convert_timestamp
from app.shared.validation import validate_base64, validate_hash, validate_url, validate_uuid

NOT_DEFINED = str(uuid.uuid4())
REQUIRED = 1
INTEGER = 2
STRING = 4
BOOLEAN = 8
UUID = 16
EXPIRE = 32
BASE64 = 64
DEVICE_TOKEN = 128
PLATFORM = 256
TIMESTAMP = 512
HASH = 1024
URL = 2048


class InputValues:
    def __init__(self, data=None):
        if not data:
            data = {}
        self._data = data

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return str(self._data)

    def __getitem__(self, key):
        return self._data.get(key)

    def __getattr__(self, key):
        return self._data.get(key)

    def __contains__(self, item):
        return self._data.__contains__(item)

    def __eq__(self, other):
        if isinstance(other, InputValues):
            return self._data == other._data
        elif isinstance(other, dict):
            return self._data == other
        else:
            return False

    def update(self, *args, **kwargs):
        return self._data.update(*args, **kwargs)

    def keys(self):
        return self._data.keys()

    def get(self, key, default=None):
        return self._data.get(key, default)


class Schema:
    def __init__(self, **kwargs):
        schema_map = {}
        key_map = {}
        for k, v in kwargs.items():
            schema_map[k] = v
            key_map[k.lower().replace('_', '')] = k

        self.schema_map = schema_map
        self.key_map = key_map

    async def load(self, input_data):
        values = InputValues()

        try:
            if input_data and isinstance(input_data, bytes):
                input_data = input_data.decode('utf-8')
            if input_data and isinstance(input_data, str):
                try:
                    input_data = json.loads(input_data)
                except Exception:
                    values.update(error='Invalid JSON')
                    return values
            if input_data and not isinstance(input_data, dict):
                values.update(error='Invalid input data')
                return values
        except Exception:
            values.update(error='Invalid input data')
            return values

        mapped_values = {}
        if input_data:
            for key, value in input_data.items():
                if key.lower() in self.key_map:
                    key = self.key_map[key.lower()]
                if key not in self.schema_map:
                    values.update(error=f'Unknown input: {key}')
                    return values
                mapped_values[key] = value

        for key, definition in self.schema_map.items():
            default = None
            if isinstance(definition, tuple):
                definition, default = definition

            value = mapped_values.get(key, NOT_DEFINED)
            external_key = camel_case(key)

            if definition & REQUIRED == REQUIRED and value in (NOT_DEFINED, None, '', [], {}):
                values.update(error=f'Missing required input: {external_key}')
                return values

            if value in (NOT_DEFINED, None, '', [], {}):
                if callable(default):
                    value = await async_call(default())
                else:
                    value = default

            if definition & TIMESTAMP == TIMESTAMP and value is not None:
                ts = convert_timestamp(str(value))
                if not ts or ts > datetime.datetime.utcnow() + datetime.timedelta(seconds=60):
                    values.update(error=f'Invalid timestamp value: {external_key}')
                    return values
                value = ts

            if definition & HASH == HASH and value is not None:
                value = str(value).lower()
                if not validate_hash(value):
                    values.update(error=f'Invalid SHA3-256 hashed value: {external_key}')
                    return values

            if definition & UUID == UUID and value is not None:
                value = str(value).lower()
                if not validate_uuid(value):
                    values.update(error=f'Invalid UUID value: {external_key}')
                    return values

            if definition & INTEGER == INTEGER and value is not None:
                try:
                    value = int(value)
                except Exception:
                    values.update(error=f'Invalid integer value: {external_key}')
                    return values

            if definition & BOOLEAN == BOOLEAN and value is not True and value is not False:
                try:
                    value = bool(int(value))
                except Exception:
                    values.update(error=f'Invalid boolean value: {external_key}')
                    return values

            if definition & URL == URL and value:
                if not validate_url(str(value).lower()):
                    values.update(error=f'Invalid url value: {external_key}')
                    return values

            if definition & PLATFORM == PLATFORM and value:
                value = str(value).lower()
                if str(value).lower() not in ('apns', 'fcm'):
                    values.update(error=f'Invalid platform value: {external_key}')
                    return values

            if definition & DEVICE_TOKEN == DEVICE_TOKEN and value:
                value = str(value)
                if not str:
                    # not implemented
                    values.update(error=f'Invalid device token value: {external_key}')
                    return values

            if definition & EXPIRE == EXPIRE and value is not None:
                try:
                    value = int(value)
                    if value < 30 or value > 300:
                        raise Exception('Invalid value')
                except Exception:
                    values.update(error=f'Invalid expire value: {external_key}')
                    return values

            if definition & BASE64 == BASE64 and value is not None:
                try:
                    if not validate_base64(str(value).encode('utf-8')):
                        raise Exception('Invalid value')
                except Exception:
                    values.update(error=f'Invalid base64 encoded value: {external_key}')
                    return values

            values.update(**{key: value})

        return values
