import asyncio
import datetime
import json
import re
import uuid

from app.shared.utils import convert_timestamp, validate_hash, validate_validation_code, validate_url


async def handler(event, context):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, json.dumps({'error': 'Invalid payload'})

    secret_hash = str(payload.get('secretHash', '')).lower() or str(payload.get('secrethash', '')).lower() or str(payload.get('secret_hash', '')).lower() or str(payload.get('hash', '')).lower()
    ip = str(payload.get('ip', '')) or None
    issuer = str(payload.get('issuer', '')) or None
    username = str(payload.get('username', '')) or None
    validation_code = str(payload.get('validationCode', '')) or str(payload.get('validationcode', '')) or str(payload.get('validation_code', '')) or str(payload.get('code', '')) or None
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
        expire_at = timestamp_at + datetime.timedelta(seconds=int(expire))
        if not expire_at or expire_at < timestamp_at:
            raise Exception('Expire too early')
    except Exception:
        return 400, json.dumps({'error': 'Invalid value for expire'})

    if not validate_hash(secret_hash):
        return 400, json.dumps({'error': 'Invalid value for secretHash'})

    if validation_code and not validate_validation_code(validation_code):
        return 400, json.dumps({'error': 'Invalid value for validationCode'})

    prompt_identifier = str(uuid.uuid4())

    location = 'Unknown'

    store_data = {
        'promptIdentifier': prompt_identifier,
        'state': 'pending',
        'secretHash': secret_hash,
        'issuer': issuer,
        'username': username,
        'validationCode': validation_code,
        'ip': ip,
        'location': location,
        'timestamp': timestamp_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        'expireAt': expire_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        'approveUrl': 'https://api.require.id/poll/response',
        'webhookUrl': webhook_url
    }

    data = {
        'promptIdentifier': prompt_identifier
    }

    return 200, json.dumps(data)
