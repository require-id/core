import datetime
import json

from app.shared.data import delete, load, store
from app.shared.utils import convert_timestamp, get_query_value, validate_hash


async def handler(event, context):
    secret_hash = get_query_value(event, ('secretHash', 'secrethash', 'secret_hash', 'hash'), '').lower()

    if not validate_hash(secret_hash):
        return 400, json.dumps({'error': 'Invalid value for secretHash'})

    try:
        stored_data = json.loads(await load('user', secret_hash))
    except Exception:
        return 404, json.dumps({'error': 'No available prompt'})

    prompt_identifier = stored_data.get('promptIdentifier')
    state = 'pending' if stored_data.get('state') in ('pending', 'received') else stored_data.get('state')
    expire_at = convert_timestamp(stored_data.get('expireAt'))

    if state not in ('pending', 'expired', 'aborted'):
        await delete('user', secret_hash)
        return 404, json.dumps({'error': 'No available prompt'})

    if stored_data.get('state') in ('pending', 'received') and expire_at < datetime.datetime.now():
        state = 'expired'

        store_data = dict(stored_data)
        store_data['state'] = state

        await store('user', secret_hash, store_data)
        await store('prompt', prompt_identifier, store_data)
    elif stored_data.get('state') == 'pending':
        store_data = dict(stored_data)
        store_data['state'] = 'received'

        await store('user', secret_hash, store_data)
        await store('prompt', prompt_identifier, store_data)

    if state in ('expired', 'aborted') and expire_at + datetime.timedelta(seconds=600) < datetime.datetime.now():
        await delete('user', secret_hash)
        return 404, json.dumps({'error': 'No available prompt'})
    elif state in ('expired', 'aborted'):
        await delete('user', secret_hash)

    data = {
        'state': state,
        'encryptedData': stored_data.get('encryptedData'),
        'uniqueIdentifier': stored_data.get('uniqueIdentifier'),
        'timestamp': stored_data.get('timestamp'),
        'expireAt': stored_data.get('expireAt')
    }

    return 200, json.dumps(data)
