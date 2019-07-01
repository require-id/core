import asyncio
import datetime
import json

from app.shared.data import load, store
from app.shared.utils import convert_timestamp, get_query_value, validate_uuid


async def handler(event, context):
    prompt_identifier = get_query_value(event, ('promptIdentifier', 'promptidentifier', 'prompt_identifier', 'identifier'), '').lower()

    if not validate_uuid(prompt_identifier):
        return 400, json.dumps({'error': 'Invalid value for promptIdentifier'})

    try:
        stored_data = json.loads(await load(prompt_identifier, 'prompt'))
    except Exception:
        return 404, json.dumps({'error': 'No such promptIdentifier'})

    state = stored_data.get('state')
    expire_at = convert_timestamp(stored_data.get('expireAt'))

    if stored_data.get('state') in ('pending', 'received') and expire_at < datetime.datetime.now():
        secret_hash = stored_data.get('secretHash')
        state = 'expired'

        store_data = dict(stored_data)
        store_data['state'] = state

        await store(prompt_identifier, 'prompt', json.dumps(store_data).encode())
        await store(secret_hash, 'user', json.dumps(store_data).encode())

    data = {
        'state': state,
        'responseHash': stored_data.get('responseHash'),
        'timestamp': stored_data.get('timestamp'),
        'expireAt': stored_data.get('expireAt'),
        'respondedAt': stored_data.get('respondedAt')
    }

    return 200, json.dumps(data)
