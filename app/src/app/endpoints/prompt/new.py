import datetime
import json
import re
import uuid

from app.shared.data import load, store
from app.shared.utils import convert_timestamp, get_payload_value, validate_base64, validate_hash, validate_validation_code, validate_url


async def handler(event, context):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, json.dumps({'error': 'Invalid payload'})

    secret_hash = get_payload_value(payload, ('secretHash', 'secrethash', 'secret_hash', 'hash'), '').lower()
    timestamp = get_payload_value(payload, 'timestamp')
    expire = get_payload_value(payload, 'expire', 90)

    ip = get_payload_value(payload, 'ip')
    location = get_payload_value(payload, 'location')
    issuer = get_payload_value(payload, 'issuer')
    username = get_payload_value(payload, 'username')
    validation_code = get_payload_value(payload, ('validationCode', 'validationcode', 'validation_code'), '').upper() or None
    sign_key = get_payload_value(payload, ('signKey', 'signkey', 'sign_key'))
    webhook_url = get_payload_value(payload, ('webhookUrl', 'webhookurl', 'webhook_url'))

    # encryptedData may all contain: ip, location, issuer, username, validationCode, signKey and webhookUrl
    encrypted_data = get_payload_value(payload, ('encryptedData', 'encrypteddata', 'encrypted_data'))

    try:
        timestamp_at = convert_timestamp(timestamp) if timestamp else datetime.datetime.now()
        if not timestamp_at:
            return 400, json.dumps({'error': 'Invalid value for timestamp'})
    except Exception:
        return 400, json.dumps({'error': 'Invalid value for timestamp'})

    try:
        if int(expire) < 30 or int(expire) > 300:
            return 400, json.dumps({'error': 'Invalid value for expire'})
    except Exception:
        return 400, json.dumps({'error': 'Invalid value for expire'})

    try:
        expire_at = timestamp_at + datetime.timedelta(seconds=int(expire))
        if not expire_at or expire_at < timestamp_at:
            raise Exception('Expire too early')
    except Exception:
        return 400, json.dumps({'error': 'Invalid value for expire'})

    if not validate_hash(secret_hash):
        return 400, json.dumps({'error': 'Invalid value for secretHash'})

    if validation_code and not validate_validation_code(validation_code):
        return 400, json.dumps({'error': 'Invalid value for validationCode'})

    if webhook_url and not validate_url(webhook_url):
        return 400, json.dumps({'error': 'Invalid value for webhookUrl'})

    try:
        if encrypted_data and not validate_base64(encrypted_data.encode('utf-8')):
            return 400, json.dumps({'error': 'encryptedData must be base64 endcoded'})
    except Exception:
        return 400, json.dumps({'error': 'encryptedData must be base64 endcoded'})

    try:
        stored_data = json.loads(await load('user', secret_hash))
        if stored_data:
            stored_expire_at = convert_timestamp(stored_data.get('expireAt'))
            if stored_data.get('state') in ('pending', 'received') and stored_expire_at >= datetime.datetime.now():
                return 406, json.dumps({'error': 'Prompt already pending'})
    except Exception:
        pass

    prompt_identifier = str(uuid.uuid4())

    store_data = {
        'promptIdentifier': prompt_identifier,
        'state': 'pending',
        'secretHash': secret_hash,
        'issuer': issuer,
        'username': username,
        'validationCode': validation_code,
        'signKey': sign_key,
        'ip': ip,
        'location': location,
        'encryptedData': encrypted_data,
        'timestamp': timestamp_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'expireAt': expire_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'respondedAt': None,
        'responseHash': None,
        'approveUrl': 'https://api.require.id/poll/response',
        'webhookUrl': webhook_url
    }

    await store('prompt', prompt_identifier, json.dumps(store_data).encode())
    await store('user', secret_hash, json.dumps(store_data).encode())

    data = {
        'promptIdentifier': prompt_identifier,
        'state': store_data.get('state'),
        'expireAt': store_data.get('expireAt')
    }

    return 200, json.dumps(data)
