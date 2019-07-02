import json

from app.shared import schema
from app.shared.data import delete, load

SCHEMA = schema.Schema(
    prompt_user_hash=schema.HASH | schema.REQUIRED,
    device_token=schema.DEVICE_TOKEN | schema.REQUIRED,
    platform=schema.PLATFORM | schema.REQUIRED
)


async def handler(event, context):
    values = await SCHEMA.load(event.get('body'))
    if values.error:
        return 400, {'error': values.error}

    subscription_data = await load('subscription', values.prompt_user_hash)
    if not subscription_data or not isinstance(subscription_data, list):
        await delete('subscription', values.prompt_user_hash)
    else:
        store_data = []
        for subscription in subscription_data:
            if subscription.get('deviceToken') != values.device_token:
                store_data.append(subscription)
        if not store_data:
            await delete('subscription', values.prompt_user_hash)
        else:
            await store('subscription', values.prompt_user_hash, store_data)

    return 200, {
        'promptUserHash': values.prompt_user_hash,
        'deviceToken': values.device_token,
        'platform': values.platform,
        'state': 'deleted'
    }
