import asyncio
import json

from app.shared.utils import validate_uuid


async def handler(event, context, self_hosted_config=None):
    prompt_identifier = str(event.get('queryStringParameters', {}).get('promptIdentifier', '')).lower() or str(event.get('queryStringParameters', {}).get('promptidentifier', '')).lower() or str(event.get('queryStringParameters', {}).get('prompt_identifier', '')).lower() or str(event.get('queryStringParameters', {}).get('identifier', '')).lower()

    if not validate_uuid(prompt_identifier):
        return 400, json.dumps({'error': 'Invalid value for promptIdentifier'})

    # Debug data for testing purposes
    stored_data = {
        'promptIdentifier': None,
        'state': 'pending',
        'secretHash': ,
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

    stored_data['state'] = 'aborted'

    return 200, json.dumps({'message': 'Prompt aborted'})
