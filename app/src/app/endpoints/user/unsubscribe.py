import asyncio
import datetime
import json

from app.shared.data import load, delete
from app.shared.utils import convert_timestamp, get_payload_value, validate_hash, validate_device_token


async def handler(event, context, self_hosted_config=None):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, json.dumps({'error': 'Invalid payload'})

    secret_hash = get_payload_value(payload, ('secretHash', 'secrethash', 'secret_hash', 'hash'), '').lower()
    device_token = get_payload_value(payload, ('deviceToken', 'devicetoken', 'device_token', 'token'))

    if not validate_hash(secret_hash):
        return 400, json.dumps({'error': 'Invalid value for secretHash'})

    if not validate_device_token(device_token):
        return 400, json.dumps({'error': 'Invalid value for deviceToken'})

    return 400, json.dumps({'error': 'Not implemented'})
