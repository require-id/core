import datetime

from app.shared import schema
from app.shared.data import delete, load, store
from app.shared.handler import lambda_handler
from app.shared.utils import is_expired

SCHEMA = schema.Schema(
    prompt_user_hash=schema.HASH | schema.REQUIRED,
    unique_identifier=schema.UUID | schema.REQUIRED,
    approve=schema.BOOLEAN | schema.REQUIRED,
    response_hash=schema.HASH,
    webhook_url=schema.URL,
)


@lambda_handler(SCHEMA)
async def handler(values=None, **kwargs):
    stored_data = await load('user', values.prompt_user_hash)
    if not stored_data:
        return 404, {'error': 'No available prompt'}

    if stored_data.get('uniqueIdentifier') != values.unique_identifier:
        return 404, {'error': 'No available prompt'}

    if stored_data.get('state') not in ('pending', 'received'):
        return 404, {'error': 'No available prompt'}

    if is_expired(stored_data.get('expireAt')):
        return 404, {'error': 'No available prompt'}

    prompt_identifier = stored_data.get('promptIdentifier')
    state = 'approved' if values.approve else 'denied'
    responded_at = datetime.datetime.utcnow()

    store_data = dict(stored_data)
    store_data['state'] = state
    store_data['respondedAt'] = responded_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    store_data['responseHash'] = values.response_hash

    await store('prompt', prompt_identifier, store_data)
    await delete('user', values.prompt_user_hash)

    if values.webhook_url:
        request_body = {  # noqa
            'promptIdentifier': prompt_identifier,
            'respondedAt': responded_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'responseHash': values.response_hash,
            'state': state
        }

    return 200, {
        'state': state,
        'uniqueIdentifier': values.unique_identifier,
        'respondedAt': responded_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }
