import datetime
import json

from app.shared.data import load, store
from app.shared.utils import convert_timestamp, get_payload_value, validate_hash


async def handler(event, context):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, json.dumps({'error': 'Invalid payload'})

    secret_hash = get_payload_value(payload, ('secretHash', 'secrethash', 'secret_hash', 'hash'), '').lower()
    validation_code = get_payload_value(payload, ('validationCode', 'validationcode', 'validation_code'), '').upper() or None
    response_hash = get_payload_value(payload, ('responseHash', 'responsehash', 'response_hash'), '').lower() or None
    webhook_url = get_payload_value(payload, ('webhookUrl', 'webhookurl', 'webhook_url'))
    approve = payload.get('approve')

    if not validate_hash(secret_hash):
        return 400, json.dumps({'error': 'Invalid value for secretHash'})

    if response_hash and not validate_hash(response_hash):
        return 400, json.dumps({'error': 'Invalid value for responseHash'})

    if approve is not True and approve is not False:
        try:
            approve = bool(int(approve))
        except Exception:
            return 400, json.dumps({'error': 'Invalid value for approve'})

    if webhook_url and not validate_url(webhook_url):
        return 400, json.dumps({'error': 'Invalid value for webhookUrl'})

    try:
        stored_data = json.loads(await load('user', secret_hash))
    except Exception:
        return 404, json.dumps({'error': 'No available prompt'})

    expire_at = convert_timestamp(stored_data.get('expireAt'))
    expected_validation_code = stored_data.get('validationCode')
    prompt_identifier = stored_data.get('promptIdentifier')

    if stored_data.get('state') not in ('pending', 'received'):
        return 404, json.dumps({'error': 'No available prompt'})

    if expire_at < datetime.datetime.now():
        return 404, json.dumps({'error': 'No available prompt'})

    if expected_validation_code and validation_code.upper() != expected_validation_code.upper():
        return 400, json.dumps({'error': 'Invalid value for validationCode'})

    state = 'approved' if approve else 'denied'
    responded_at = datetime.datetime.now()

    store_data = dict(stored_data)
    store_data['state'] = state
    store_data['respondedAt'] = responded_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    store_data['responseHash'] = response_hash

    await store('prompt', prompt_identifier, store_data)
    await delete('user', secret_hash)

    if webhook_url and stored_data.get('webhookUrl') and webhook_url != stored_data.get('webhookUrl'):
        webhook_url = None
    elif not webhook_url and stored_data.get('webhookUrl'):
        webhook_url = stored_data.get('webhookUrl')

    if webhook_url:
        request_body = {
            'promptIdentifier': prompt_identifier,
            'respondedAt': responded_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'responseHash': response_hash,
            'validationCode': validation_code,
            'state': state
        }
        # todo

    data = {
        'state': state,
        'respondedAt': responded_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }

    return 200, json.dumps(data)
