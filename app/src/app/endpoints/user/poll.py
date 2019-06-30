import asyncio
import json

from app.shared.utils import validate_hash


async def handler(event, context, self_hosted_config=None):
    secret_hash = str(event.get('queryStringParameters', {}).get('secretHash', '')).lower() or str(event.get('queryStringParameters', {}).get('secrethash', '')).lower() or str(event.get('queryStringParameters', {}).get('secret_hash', '')).lower() or str(event.get('queryStringParameters', {}).get('hash', '')).lower()

    if not validate_hash(secret_hash):
        return 400, json.dumps({'error': 'Invalid value for secretHash'})

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

    if stored_data.get('pending') != 'pending':
        return 404, json.dumps({'error': 'No available prompt'})

    data = {
        'state': stored_data.get('state'),
        'username': stored_data.get('username'),
        'issuer': stored_data.get('issuer'),
        'validationCode': stored_data.get('validationCode'),
        'ip': stored_data.get('ip'),
        'location': stored_data.get('location'),
        'approveUrl': stored_data.get('approveUrl')
    }

    return 200, json.dumps(data)
