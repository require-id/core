import asyncio
import json

from app.shared.utils import convert_timestamp, validate_hash, validate_device_token


async def handler(event, context):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, json.dumps({'error': 'Invalid payload'})

    secret_hash = str(payload.get('secretHash', '')).lower() or str(payload.get('secrethash', '')).lower() or str(payload.get('secret_hash', '')).lower() or str(payload.get('hash', '')).lower()
    timestamp = str(payload.get('timestamp', '')) or None
    device_token = str(payload.get('deviceToken', '')) or str(payload.get('devicetoken', '')) or str(payload.get('device_token', '')) or str(payload.get('token', '')) or None

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

    store_data = {
        'secretHash': secret_hash,
        'deviceToken': device_token
    }

    return 400, json.dumps({'error': 'Not implemented'})
