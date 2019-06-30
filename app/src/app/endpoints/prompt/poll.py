import asyncio
import json

from app.shared.data import load
from app.shared.utils import validate_uuid


async def handler(event, context, self_hosted_config=None):
    prompt_identifier = str(event.get('queryStringParameters', {}).get('promptIdentifier', '')).lower() or str(event.get('queryStringParameters', {}).get('promptidentifier', '')).lower() or str(event.get('queryStringParameters', {}).get('prompt_identifier', '')).lower() or str(event.get('queryStringParameters', {}).get('identifier', '')).lower()

    if not validate_uuid(prompt_identifier):
        return 400, json.dumps({'error': 'Invalid value for promptIdentifier'})

    stored_data = json.loads(await load(prompt_identifier, 'prompt', self_hosted_config=self_hosted_config))

    data = {
        'state': stored_data.get('state'),
        'timestamp': stored_data.get('timestamp'),
        'expireAt': stored_data.get('expireAt'),
    }

    return 200, json.dumps(data)
