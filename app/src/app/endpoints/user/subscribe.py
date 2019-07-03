from app.shared import schema
from app.shared.data import load, store
from app.shared.handler import lambda_handler

SCHEMA = schema.Schema(
    prompt_user_hash=schema.HASH | schema.REQUIRED,
    device_token=schema.DEVICE_TOKEN | schema.REQUIRED,
    platform=schema.PLATFORM | schema.REQUIRED
)


@lambda_handler(SCHEMA)
async def handler(values=None, **kwargs):
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
