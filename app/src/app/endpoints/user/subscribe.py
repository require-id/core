import datetime
import json

from app.shared.data import store
from app.shared.utils import convert_timestamp, get_payload_value, validate_hash, validate_device_token


async def handler(event, context):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, json.dumps({'error': 'Invalid payload'})

    secret_hash = get_payload_value(payload, ('secretHash', 'secrethash', 'secret_hash', 'hash'), '').lower()
    timestamp = get_payload_value(payload, 'timestamp')
    device_token = get_payload_value(payload, ('deviceToken', 'devicetoken', 'device_token', 'token'))
    platform = get_payload_value(payload, 'platform')

    if not validate_hash(secret_hash):
        return 400, json.dumps({'error': 'Invalid value for secretHash'})

    if not validate_device_token(device_token):
        return 400, json.dumps({'error': 'Invalid value for deviceToken'})

    try:
        timestamp_at = convert_timestamp(timestamp) if timestamp else datetime.datetime.now()
        if not timestamp_at:
            return 400, json.dumps({'error': 'Invalid value for timestamp'})
    except Exception:
        return 400, json.dumps({'error': 'Invalid value for timestamp'})

    if not platform or platform not in ('apns', 'fcm'):
        return 400, json.dumps({'error': 'Invalid value for platform'})

    store_data = {
        'secretHash': secret_hash,
        'deviceToken': device_token,
        'platform': platform,
        'state': 'subscribed'
    }

    await store('subscription', f'{platform}-{secret_hash}', store_data)

    return 200, json.dumps(store_data)
