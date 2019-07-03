from app.shared import schema
from app.shared.data import load, store
from app.shared.handler import lambda_handler
from app.shared.utils import is_expired

SCHEMA = schema.Schema(
    prompt_identifier=schema.UUID | schema.REQUIRED
)


@lambda_handler(SCHEMA)
async def handler(values=None, **kwargs):
    stored_data = await load('prompt', values.prompt_identifier)
    if not stored_data:
        return 404, {'error': 'No such promptIdentifier'}

    state = stored_data.get('state')

    if stored_data.get('state') in ('pending', 'received') and is_expired(stored_data.get('expireAt')):
        prompt_user_hash = stored_data.get('promptUserHash')
        state = 'expired'

        store_data = dict(stored_data)
        store_data['state'] = state

        await store('prompt', values.prompt_identifier, store_data)
        await store('user', prompt_user_hash, store_data)

    return 200, {
        'state': state,
        'responseHash': stored_data.get('responseHash'),
        'timestamp': stored_data.get('timestamp'),
        'expireAt': stored_data.get('expireAt'),
        'respondedAt': stored_data.get('respondedAt')
    }
