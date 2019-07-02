import datetime
import json
import uuid

from app.shared.data import load, store
from app.shared.utils import convert_timestamp, get_payload_value, sha3, validate_base64, validate_hash, validate_url


async def handler(event, context):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, {'error': 'Invalid payload'}

    prompt_user_hash = get_payload_value(payload, ('promptUserHash', 'userHash', 'hash'), '').lower()
    timestamp = get_payload_value(payload, 'timestamp')
    expire = get_payload_value(payload, 'expire', 90)

    # encryptedData contains: ip, location, issuer, username, validationCode, signKey, timestamp, expire and webhookUrl
    # Device should verify that timestamp and expire match values in poll to prevent replay attacks with other values
    encrypted_data = get_payload_value(payload, ('encryptedData', 'data'))

    try:
        timestamp_at = convert_timestamp(timestamp) if timestamp else datetime.datetime.now()
        if not timestamp_at:
            return 400, {'error': 'Invalid value for timestamp'}
    except Exception:
        return 400, {'error': 'Invalid value for timestamp'}

    try:
        if int(expire) < 30 or int(expire) > 300:
            return 400, {'error': 'Invalid value for expire'}
    except Exception:
        return 400, {'error': 'Invalid value for expire'}

    try:
        expire_at = timestamp_at + datetime.timedelta(seconds=int(expire))
        if not expire_at or expire_at < timestamp_at:
            raise Exception('Expire too early')
    except Exception:
        return 400, {'error': 'Invalid value for expire'}

    if not validate_hash(prompt_user_hash):
        return 400, {'error': 'Invalid value for promptUserHash'}

    try:
        if encrypted_data and not validate_base64(encrypted_data.encode('utf-8')):
            return 400, {'error': 'encryptedData must be base64 endcoded'}
    except Exception:
        return 400, {'error': 'encryptedData must be base64 endcoded'}

    try:
        stored_data = await load('user', prompt_user_hash)
        if stored_data:
            if stored_data.get('state') in ('pending', 'received') and convert_timestamp(stored_data.get('expireAt')) >= datetime.datetime.now():
                return 406, {'error': 'Prompt already pending'}
            if sha3(stored_data.get('encryptedData')) == sha3(encryptedData):
                return 406, {'error': 'Prompt already sent'}
    except Exception:
        pass

    prompt_identifier = str(uuid.uuid4())

    store_data = {
        'promptIdentifier': prompt_identifier,
        'promptUserHash': prompt_user_hash,
        'uniqueIdentifier': str(uuid.uuid4()),
        'state': 'pending',
        'encryptedData': encrypted_data,
        'timestamp': timestamp_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'expireAt': expire_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'respondedAt': None,
        'responseHash': None
    }

    await store('prompt', prompt_identifier, store_data)
    await store('user', prompt_user_hash, store_data)

    subscription_data = await load('subscription', prompt_user_hash)  # noqa
    if subscription_data and isinstance(subscription_data, list):
        for subscription in subscription_data:
            if subscription.get('promptUserHash') == prompt_user_hash:
                # todo send notification
                pass

    return 200, {
        'promptIdentifier': prompt_identifier,
        'state': store_data.get('state'),
        'expireAt': store_data.get('expireAt')
    }
