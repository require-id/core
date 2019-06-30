import asyncio
import json

from app.shared.data import load, store
from app.shared.utils import convert_timestamp, validate_uuid


async def handler(event, context, self_hosted_config=None):
    prompt_identifier = str(event.get('queryStringParameters', {}).get('promptIdentifier', '')).lower() or str(event.get('queryStringParameters', {}).get('promptidentifier', '')).lower() or str(event.get('queryStringParameters', {}).get('prompt_identifier', '')).lower() or str(event.get('queryStringParameters', {}).get('identifier', '')).lower()

    if not validate_uuid(prompt_identifier):
        return 400, json.dumps({'error': 'Invalid value for promptIdentifier'})

    stored_data = json.loads(await load(prompt_identifier, 'prompt', self_hosted_config=self_hosted_config))

    if stored_data.get('state') not in ('pending', 'received'):
        return 406, json.dumps({'error': 'Prompt is not in pending state'})

    secret_hash = stored_data.get('secretHash')

    store_data = dict(stored_data)
    store_data['state'] = 'aborted'

    await store(prompt_identifier, 'prompt', json.dumps(store_data).encode(), self_hosted_config=self_hosted_config)
    await store(secret_hash, 'user', json.dumps(store_data).encode(), self_hosted_config=self_hosted_config)

    data = {
        'promptIdentifier': prompt_identifier,
        'state': store_data.get('state')
    }

    return 200, json.dumps(data)
