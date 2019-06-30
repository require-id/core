import asyncio
import datetime
import json
import re
import uuid

from app.shared.data import load, store
from app.shared.utils import convert_timestamp, validate_hash, validate_validation_code, validate_url


async def handler(event, context, self_hosted_config=None):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, json.dumps({'error': 'Invalid payload'})

    secret_hash = str(payload.get('secretHash', '')).lower() or str(payload.get('secrethash', '')).lower() or str(payload.get('secret_hash', '')).lower() or str(payload.get('hash', '')).lower()
    ip = str(payload.get('ip', '')) or None
    issuer = str(payload.get('issuer', '')) or None
    username = str(payload.get('username', '')) or None
    validation_code = str(payload.get('validationCode', '')) or str(payload.get('validationcode', '')) or str(payload.get('validation_code', '')) or None
    sign_key = str(payload.get('signKey', '')) or str(payload.get('signkey', '')) or str(payload.get('sign_key', '')) or None
    timestamp = str(payload.get('timestamp', '')) or None
    expire = str(payload.get('expire', '')) or 90
    webhook_url = str(payload.get('webhookUrl', '')) or str(payload.get('webhookurl', '')) or str(payload.get('webhook_url', '')) or None

    if webhook_url and not validate_url(webhook_url):
        return 400, json.dumps({'error': 'Invalid value for webhookUrl'})

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

    stored_data = json.loads(await load(secret_hash, 'user', self_hosted_config=self_hosted_config))
    if stored_data:
        stored_expire_at = convert_timestamp(stored_data.get('expireAt'))
        if stored_data.get('state') in ('pending', 'received') and stored_expire_at >= datetime.datetime.now():
            return 406, json.dumps({'error': 'Prompt already pending'})

    location = 'Unknown'
    prompt_identifier = str(uuid.uuid4())
    response_code = str(uuid.uuid4())

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
        'timestamp': timestamp_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'expireAt': expire_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'respondedAt': None,
        'responseHash': None,
        'approveUrl': 'https://api.require.id/poll/response',
        'webhookUrl': webhook_url
    }

    await store(prompt_identifier, 'prompt', json.dumps(store_data).encode(), self_hosted_config=self_hosted_config)
    await store(secret_hash, 'user', json.dumps(store_data).encode(), self_hosted_config=self_hosted_config)

    data = {
        'promptIdentifier': prompt_identifier,
        'state': store_data.get('state'),
        'expireAt': store_data.get('expireAt')
    }

    return 200, json.dumps(data)
