import json

from app.shared.data import delete
from app.shared.utils import get_payload_value, validate_hash, validate_device_token


async def handler(event, context):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, json.dumps({'error': 'Invalid payload'})

    secret_hash = get_payload_value(payload, ('secretHash', 'secrethash', 'secret_hash', 'hash'), '').lower()
    device_token = get_payload_value(payload, ('deviceToken', 'devicetoken', 'device_token', 'token'))
    platform = get_payload_value(payload, 'platform')

    if not validate_hash(secret_hash):
        return 400, json.dumps({'error': 'Invalid value for secretHash'})

    if not validate_device_token(device_token):
        return 400, json.dumps({'error': 'Invalid value for deviceToken'})

    if not platform or platform not in ('apns', ):
        return 400, json.dumps({'error': 'Invalid value for platform'})

    await delete('subscription', f'{platform}-{secret_hash}')
    store_data = {
        'secretHash': secret_hash,
        'deviceToken': device_token,
        'platform': platform,
        'state': 'deleted'
    }

    return 200, json.dumps(store_data)
