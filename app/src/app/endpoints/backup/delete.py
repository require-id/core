import json

from app.shared import data
from app.shared.utils import get_query_value, validate_hash


async def handler(event, context, self_hosted_config=None):
    seed_hash = get_query_value(event, ('seedHash', 'seedhash', 'seed_hash', 'hash'), '').lower()

    if not validate_hash(seed_hash):
        return 400, json.dumps({'error': 'Invalid value for seedHash'})

    await data.delete(seed_hash, 'backup', self_hosted_config=self_hosted_config)

    return 200, json.dumps({'state': 'deleted'})
