import json

from app.shared.data import load
from app.shared.utils import get_query_value, validate_hash


async def handler(event, context):
    seed_hash = get_query_value(event, ('seedHash', 'seedhash', 'seed_hash', 'hash'), '').lower()

    if not validate_hash(seed_hash):
        return 400, json.dumps({'error': 'Invalid value for seedHash'})

    backup_data = await load('backup', seed_hash)

    if backup_data:
        return 200, json.dumps({'state': 'saved', 'backupData': backup_data.decode('utf-8')})

    return 404, json.dumps({'error': 'No such seedHash'})
