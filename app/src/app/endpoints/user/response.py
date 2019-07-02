import datetime
import json

from app.shared.data import delete, load, store
from app.shared.utils import convert_timestamp, get_payload_value, validate_hash, validate_url


async def handler(event, context):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, {'error': 'Invalid payload'}

    prompt_user_hash = get_payload_value(payload, ('promptUserHash', 'promptuserhash', 'prompt_user_hash', 'userHash', 'userhash', 'user_hash', 'hash'), '').lower()
    unique_identifier = get_payload_value(payload, ('uniqueIdentifier', 'uniqueidentifier', 'unique_identifier', 'identifier'), '').lower()
    response_hash = get_payload_value(payload, ('responseHash', 'responsehash', 'response_hash'), '').lower() or None
    webhook_url = get_payload_value(payload, ('webhookUrl', 'webhookurl', 'webhook_url'))
    approve = payload.get('approve')

    if not validate_hash(prompt_user_hash):
        return 400, {'error': 'Invalid value for promptUserHash'}

    if response_hash and not validate_hash(response_hash):
        return 400, {'error': 'Invalid value for responseHash'}

    if approve is not True and approve is not False:
        try:
            approve = bool(int(approve))
        except Exception:
            return 400, {'error': 'Invalid value for approve'}

    if webhook_url and not validate_url(webhook_url):
        return 400, {'error': 'Invalid value for webhookUrl'}

    try:
        stored_data = await load('user', prompt_user_hash)
        if not stored_data:
            return 404, {'error': 'No available prompt'}
    except Exception:
        return 404, {'error': 'No available prompt'}

    if not unique_identifier or stored_data.get('uniqueIdentifier') != unique_identifier:
        return 404, {'error': 'No available prompt'}

    if stored_data.get('state') not in ('pending', 'received'):
        return 404, {'error': 'No available prompt'}

    expire_at = convert_timestamp(stored_data.get('expireAt'))

    if expire_at < datetime.datetime.now():
        return 404, {'error': 'No available prompt'}

    prompt_identifier = stored_data.get('promptIdentifier')
    state = 'approved' if approve else 'denied'
    responded_at = datetime.datetime.now()

    store_data = dict(stored_data)
    store_data['state'] = state
    store_data['respondedAt'] = responded_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    store_data['responseHash'] = response_hash

    await store('prompt', prompt_identifier, store_data)
    await delete('user', prompt_user_hash)

    if webhook_url:
        request_body = {  # noqa
            'promptIdentifier': prompt_identifier,
            'respondedAt': responded_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'responseHash': response_hash,
            'state': state
        }

    return 200, {
        'state': state,
        'uniqueIdentifier': unique_identifier,
        'respondedAt': responded_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }
