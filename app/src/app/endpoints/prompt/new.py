import asyncio
import datetime
import json
import re
import uuid

from app.shared.utils import convert_timestamp, validate_hash, validate_validation_code


async def handler(event, context):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, json.dumps({'error': 'Invalid payload'})

    secret_hash = str(payload.get('secretHash', '')).lower() or str(payload.get('secrethash', '')).lower() or str(payload.get('secret_hash', '')).lower()
    ip = str(payload.get('ip', '')) or None
    issuer = str(payload.get('issuer', '')) or None
    username = str(payload.get('username', '')) or None
    validation_code = str(payload.get('validationCode', '')) or str(payload.get('validationcode', '')) or str(payload.get('validation_code', '')) or None
    timestamp = str(payload.get('timestamp', '')) or None
    expire = str(payload.get('expire', '')) or 90
    webhook_url = str(payload.get('webhookUrl', '')) or str(payload.get('webhookurl', '')) or str(payload.get('webhook_url', '')) or None

    if webhook_url and not re.match(r'^(http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,}(:[0-9]{1,5})?(\/.*)?$', webhook_url.lower()):
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
    return 200, json.dumps({'promptIdentifier': prompt_identifier})
