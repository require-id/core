import datetime
import json

from app.shared import schema
from app.shared.data import store

SCHEMA = schema.Schema(
    prompt_user_hash=schema.HASH | schema.REQUIRED,
    device_token=schema.DEVICE_TOKEN | schema.REQUIRED,
    platform=schema.PLATFORM | schema.REQUIRED
)


async def handler(event, context):
    values = await SCHEMA.load(event.get('body'))
    if values.error:
        return 400, {'error': values.error}

    data = {
        'promptUserHash': values.prompt_user_hash,
        'deviceToken': values.device_token,
        'platform': values.platform,
        'state': 'subscribed'
    }

    subscription_data = await load('subscription', values.prompt_user_hash)
    add_store_data = True
    if not subscription_data or not isinstance(subscription_data, list):
        store_data = []
    else:
        store_data = list(subscription_data)
        for subscription in subscription_data:
            if subscription.get('deviceToken') == values.device_token:
                add_store_data = False

    if add_store_data:
        store_data.append(data)

    await store('subscription', values.prompt_user_hash, store_data)

    return 200, data
