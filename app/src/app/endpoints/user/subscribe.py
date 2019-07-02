import datetime
import json

from app.shared.data import store
from app.shared.utils import convert_timestamp, get_payload_value, validate_hash, validate_device_token


async def handler(event, context):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, {'error': 'Invalid payload'}

    prompt_user_hash = get_payload_value(payload, ('promptUserHash', 'userHash', 'hash'), '').lower()
    device_token = get_payload_value(payload, ('deviceToken', 'token'))
    platform = get_payload_value(payload, 'platform')

    if not validate_hash(prompt_user_hash):
        return 400, {'error': 'Invalid value for promptUserHash'}

    if not validate_device_token(device_token):
        return 400, {'error': 'Invalid value for deviceToken'}

    if not platform or platform not in ('apns', 'fcm'):
        return 400, {'error': 'Invalid value for platform'}

    data = {
        'promptUserHash': prompt_user_hash,
        'deviceToken': device_token,
        'platform': platform,
        'state': 'subscribed'
    }

    subscription_data = await load('subscription', prompt_user_hash)
    add_store_data = True
    if not subscription_data or not isinstance(subscription_data, list):
        store_data = []
    else:
        store_data = list(subscription_data)
        for subscription in subscription_data:
            if subscription.get('deviceToken') == device_token:
                add_store_data = False

    if add_store_data:
        store_data.append(data)

    await store('subscription', prompt_user_hash, store_data)

    return 200, data
