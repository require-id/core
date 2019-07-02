from app.shared.data import load, store
from app.shared.utils import get_query_value, validate_uuid


async def handler(event, context):
    prompt_identifier = get_query_value(event, ('promptIdentifier', 'identifier'), '').lower()

    if not validate_uuid(prompt_identifier):
        return 400, {'error': 'Invalid value for promptIdentifier'}

    try:
        stored_data = await load('prompt', prompt_identifier)
        if not stored_data:
            return 404, {'error': 'No such promptIdentifier'}
        if stored_data.get('state') not in ('pending', 'received'):
            return 406, {'error': 'Prompt is not in pending state'}
    except Exception:
        return 404, {'error': 'No such promptIdentifier'}

    prompt_user_hash = stored_data.get('promptUserHash')
    state = 'aborted'

    store_data = dict(stored_data)
    store_data['state'] = state

    await store('prompt', prompt_identifier, store_data)
    await store('user', prompt_user_hash, store_data)

    return 200, {
        'promptIdentifier': prompt_identifier,
        'state': state
    }
