import asyncio
import datetime
import json
import re
import uuid

from app.shared.utils import convert_timestamp, validate_hash


async def handler(event, context):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, json.dumps({'error': 'Invalid payload'})

    secrethash = str(payload.get('secrethash', '')).lower()
    ip = str(payload.get('ip', '')) or None
    issuer = str(payload.get('issuer', '')) or None
    username = str(payload.get('username', '')) or None
    validation_code = str(payload.get('validation_code', '')) or None
    timestamp = str(payload.get('timestamp', '')) or None
    expire = str(payload.get('expire', '')) or 90
    webhook_url = str(payload.get('webhook_url', '')) or None

    if webhook_url and not re.match(r'^(http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,}(:[0-9]{1,5})?(\/.*)?$', webhook_url.lower()):
        return 400, json.dumps({'error': 'Invalid value for webhook_url'})

    try:
        timestamp_at = convert_timestamp(timestamp) if timestamp else datetime.datetime.now()
        if not timestamp_at:
            return 400, json.dumps({'error': 'Invalid timestamp'})
    except Exception:
        return 400, json.dumps({'error': 'Invalid timestamp'})

    try:
        expire_at = timestamp_at + datetime.timedelta(seconds=int(expire))
        if not expire_at or expire_at < timestamp_at:
            raise Exception('expire too early')
    except Exception:
        return 400, json.dumps({'error': 'Invalid expire'})

    if not validate_hash(secrethash):
        return 400, json.dumps({'error': 'Invalid secrethash'})

    identifier = str(uuid.uuid4())
    return 200, json.dumps({'message': 'Prompt initiated', 'identifier': identifier})
