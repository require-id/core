import asyncio
import json

from app.shared.data import load, store
from app.shared.utils import validate_hash


async def handler(event, context, self_hosted_config=None):
    secret_hash = str(event.get('queryStringParameters', {}).get('secretHash', '')).lower() or str(event.get('queryStringParameters', {}).get('secrethash', '')).lower() or str(event.get('queryStringParameters', {}).get('secret_hash', '')).lower() or str(event.get('queryStringParameters', {}).get('hash', '')).lower()

    if not validate_hash(secret_hash):
        return 400, json.dumps({'error': 'Invalid value for secretHash'})

    stored_data = json.loads(await load(secret_hash, 'user', self_hosted_config=self_hosted_config))
    prompt_identifier = stored_data.get('promptIdentifier')

    if stored_data.get('state') not in ('pending', 'received'):
        return 404, json.dumps({'error': 'No available prompt'})

    if stored_data.get('state') == 'pending':
        store_data = dict(stored_data)
        store_data['state'] = 'received'

        await store(secret_hash, 'user', json.dumps(store_data).encode(), self_hosted_config=self_hosted_config)
        await store(prompt_identifier, 'prompt', json.dumps(store_data).encode(), self_hosted_config=self_hosted_config)

    data = {
        'state': 'pending' if stored_data.get('state') in ('pending', 'received') else stored_data.get('state'),
        'username': stored_data.get('username'),
        'issuer': stored_data.get('issuer'),
        'validationCode': stored_data.get('validationCode'),
        'ip': stored_data.get('ip'),
        'location': stored_data.get('location'),
        'approveUrl': stored_data.get('approveUrl')
    }

    return 200, json.dumps(data)
