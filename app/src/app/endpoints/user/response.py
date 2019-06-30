import asyncio
import json


async def handler(event, context):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, json.dumps({'error': 'Invalid payload'})

    secret_hash = str(payload.get('secretHash', '')).lower()
    timestamp = str(payload.get('timestamp', '')) or None
    validation_code = str(payload.get('validationCode', '')) or None
    approve = payload.get('approve')

    if not validate_hash(secrethash):
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

    expected_validation_code = ''  # debug
    if expected_validation_code and validation_code.upper() != expected_validation_code.upper():
        return 400, json.dumps({'error': 'Invalid value for validationCode'})

    return 200, json.dumps({'message': 'Prompt responded'})
