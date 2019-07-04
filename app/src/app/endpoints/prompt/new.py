import datetime
import uuid

from app.shared import schema
from app.shared.data import load, store
from app.shared.handler import lambda_handler
from app.shared.utils import is_expired, sha3

SCHEMA = schema.Schema(
    prompt_user_hash=schema.HASH | schema.REQUIRED,
    timestamp=(schema.TIMESTAMP, lambda: datetime.datetime.utcnow()),
    expire=(schema.EXPIRE, 90),
    encrypted_data=schema.BASE64
)


@lambda_handler(SCHEMA)
async def handler(values=None, **kwargs):
    try:
        expire_at = values.timestamp + datetime.timedelta(seconds=int(values.expire))
    except Exception:
        return 400, {'error': 'Invalid value for expire'}

    try:
        stored_data = await load('user', values.prompt_user_hash)
        if stored_data:
            if stored_data.get('state') in ('pending', 'received') and not is_expired(stored_data.get('expireAt')):
                return 406, {'error': 'Prompt already pending'}
            if values.encrypted_data and sha3(stored_data.get('encryptedData')) == sha3(values.encrypted_data):
                return 406, {'error': 'Prompt already sent'}
    except Exception:
        pass

    prompt_identifier = str(uuid.uuid4())

    store_data = {
        'promptIdentifier': prompt_identifier,
        'promptUserHash': values.prompt_user_hash,
        'uniqueIdentifier': str(uuid.uuid4()),
        'state': 'pending',
        'encryptedData': values.encrypted_data,
        'timestamp': values.timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'expireAt': expire_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'respondedAt': None,
        'responseHash': None
    }

    await store('prompt', prompt_identifier, store_data)
    await store('user', values.prompt_user_hash, store_data)

    subscription_data = await load('subscription', values.prompt_user_hash)  # noqa
    if subscription_data and isinstance(subscription_data, list):
        for subscription in subscription_data:
            if subscription.get('promptUserHash') == values.prompt_user_hash:
                # todo send notification
                pass

    return 200, {
        'promptIdentifier': prompt_identifier,
        'state': store_data.get('state'),
        'expireAt': store_data.get('expireAt')
    }
