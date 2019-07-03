import datetime

from app.shared import schema
from app.shared.data import delete, load, store
from app.shared.handler import lambda_handler
from app.shared.utils import convert_timestamp, is_expired

SCHEMA = schema.Schema(
    prompt_user_hash=schema.HASH | schema.REQUIRED,
)


@lambda_handler(SCHEMA)
async def handler(values=None, **kwargs):
    stored_data = await load('user', values.prompt_user_hash)
    if not stored_data:
        return 404, {'error': 'No available prompt'}

    prompt_identifier = stored_data.get('promptIdentifier')
    state = 'pending' if stored_data.get('state') in ('pending', 'received') else stored_data.get('state')
    expire_at = convert_timestamp(stored_data.get('expireAt'))

    if state not in ('pending', 'expired', 'aborted'):
        await delete('user', values.prompt_user_hash)
        return 404, {'error': 'No available prompt'}

    if stored_data.get('state') in ('pending', 'received') and is_expired(expire_at):
        state = 'expired'

        store_data = dict(stored_data)
        store_data['state'] = state

        await store('prompt', prompt_identifier, store_data)
    elif stored_data.get('state') == 'pending':
        store_data = dict(stored_data)
        store_data['state'] = 'received'

        await store('user', values.prompt_user_hash, store_data)
        await store('prompt', prompt_identifier, store_data)

    if state in ('expired', 'aborted') and is_expired(expire_at + datetime.timedelta(seconds=600)):
        await delete('user', values.prompt_user_hash)
        return 404, {'error': 'No available prompt'}
    elif state in ('expired', 'aborted'):
        await delete('user', values.prompt_user_hash)

    return 200, {
        'state': state,
        'encryptedData': stored_data.get('encryptedData'),
        'uniqueIdentifier': stored_data.get('uniqueIdentifier'),
        'timestamp': stored_data.get('timestamp'),
        'expireAt': stored_data.get('expireAt')
    }
