import asyncio
import datetime
import json

from app.shared.data import load, store
from app.shared.utils import convert_timestamp, validate_hash


async def handler(event, context, self_hosted_config=None):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, json.dumps({'error': 'Invalid payload'})

    secret_hash = str(payload.get('secretHash', '')).lower() or str(payload.get('secrethash', '')).lower() or str(payload.get('secret_hash', '')).lower() or str(payload.get('hash', '')).lower()
    timestamp = str(payload.get('timestamp', '')) or None
    validation_code = str(payload.get('validationCode', '')) or str(payload.get('validationcode', '')) or str(payload.get('validation_code', '')) or str(payload.get('code', '')) or None
    approve = payload.get('approve')

    if not validate_hash(secret_hash):
        return 400, json.dumps({'error': 'Invalid value for secretHash'})

    try:
        timestamp_at = convert_timestamp(timestamp) if timestamp else datetime.datetime.now()
        if not timestamp_at:
            return 400, json.dumps({'error': 'Invalid value for timestamp'})
    except Exception:
        return 400, json.dumps({'error': 'Invalid value for timestamp'})

    if approve is not True and approve is not False:
        try:
            approve = bool(int(approve))
        except Exception:
            return 400, json.dumps({'error': 'Invalid value for approve'})

    stored_data = json.loads(await load(secret_hash, 'user', self_hosted_config=self_hosted_config))
    expire_at = convert_timestamp(stored_data.get('expireAt'))
    expected_validation_code = stored_data.get('validationCode')
    prompt_identifier = stored_data.get('promptIdentifier')

    if stored_data.get('state') not in ('pending', 'received'):
        return 404, json.dumps({'error': 'No available prompt'})

    if expire_at < datetime.datetime.now():
        return 404, json.dumps({'error': 'No available prompt'})

    if expected_validation_code and validation_code.upper() != expected_validation_code.upper():
        return 400, json.dumps({'error': 'Invalid value for validationCode'})

    store_data = dict(stored_data)
    store_data['state'] = 'approved' if approve else 'denied'
    store_data['respondedAt'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    await store(secret_hash, 'user', json.dumps(store_data).encode(), self_hosted_config=self_hosted_config)
    await store(prompt_identifier, 'prompt', json.dumps(store_data).encode(), self_hosted_config=self_hosted_config)

    return 200, json.dumps({'message': 'Prompt responded'})
