import asyncio
import json

from app.shared.utils import validate_uuid


async def handler(event, context):
    prompt_identifier = str(event.get('queryStringParameters', {}).get('promptIdentifier', '')).lower() or str(event.get('queryStringParameters', {}).get('promptidentifier', '')).lower() or str(event.get('queryStringParameters', {}).get('prompt_identifier', '')).lower() or str(event.get('queryStringParameters', {}).get('identifier', '')).lower()

    if not validate_uuid(prompt_identifier):
        return 400, json.dumps({'error': 'Invalid value for promptIdentifier'})

    return 200, json.dumps({'message': 'Prompt aborted'})
