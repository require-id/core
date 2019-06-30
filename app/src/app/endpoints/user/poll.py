import asyncio
import json


async def handler(event, context):
    secret_hash = str(event.get('queryStringParameters', {}).get('secretHash', '')).lower() or str(event.get('queryStringParameters', {}).get('secrethash', '')).lower() or str(event.get('queryStringParameters', {}).get('secret_hash', '')).lower()

    if not validate_hash(secret_hash):
        return 400, json.dumps({'error': 'Invalid value for secrethash'})

    # Debug data for testing purposes
    data = {
        'issuer': 'The High Table',
        'username': 'john.wick@thecontentinental.hotel',
        'validationCode': 'KC3X9',
        'ip': '1.1.1.1',
        'location': 'Unknown',
        'approveUrl': 'https://api.require.id/poll/response'
    }

    return 200, json.dumps(data)
