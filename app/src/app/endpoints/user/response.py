import asyncio
import json

from app.shared.utils import convert_timestamp, validate_hash


async def handler(event, context):
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

    # Debug data for testing purposes
    stored_data = {
        'promptIdentifier': None,
        'state': 'pending',
        'issuer': 'The High Table',
        'username': 'john.wick@thecontentinental.hotel',
        'validationCode': 'KC3X9',
        'ip': '1.1.1.1',
        'location': 'Unknown',
        'timestamp': '2019-06-30T17:20:00.000000Z',
        'expireAt': '2019-06-30T17:21:30.000000Z',
        'approveUrl': 'https://api.require.id/poll/response',
        'webhookUrl': None
    }

    expected_validation_code = data.get('validationCode')
    if expected_validation_code and validation_code.upper() != expected_validation_code.upper():
        return 400, json.dumps({'error': 'Invalid value for validationCode'})

    stored_data['state'] = 'approved' if approve else 'denied'

    return 200, json.dumps({'message': 'Prompt responded'})
