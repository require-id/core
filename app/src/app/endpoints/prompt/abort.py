from app.shared import schema
from app.shared.data import load, store
from app.shared.handler import lambda_handler

SCHEMA = schema.Schema(
    prompt_identifier=schema.UUID | schema.REQUIRED
)


@lambda_handler(SCHEMA)
async def handler(values=None, **kwargs):
    stored_data = await load('prompt', values.prompt_identifier)
    if not stored_data:
        return 404, {'error': 'No such promptIdentifier'}
    if stored_data.get('state') not in ('pending', 'received'):
        return 406, {'error': 'Prompt is not in pending state'}

    prompt_user_hash = stored_data.get('promptUserHash')
    state = 'aborted'

    store_data = dict(stored_data)
    store_data['state'] = state

    await store('prompt', values.prompt_identifier, store_data)
    await store('user', prompt_user_hash, store_data)

    return 200, {
        'promptIdentifier': values.prompt_identifier,
        'state': state
    }
