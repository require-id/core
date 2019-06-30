import json

from app.shared.data import store
from app.shared.utils import get_payload_value, validate_base64, validate_hash


async def handler(event, context, self_hosted_config=None):
    try:
        payload = json.loads(event.get('body'))
    except Exception:
        return 400, json.dumps({'error': 'Invalid payload'})

    seed_hash = get_payload_value(payload, ('seedHash', 'seedhash', 'seed_hash', 'hash'), '').lower()
    backup_data = get_payload_value(payload, ('backupData', 'backupdata', 'backup_data', 'data'), '')

    if not validate_hash(seed_hash):
        return 400, json.dumps({'error': 'Invalid value for seedHash'})

    try:
        if not validate_base64(backup_data.encode('utf-8')):
            return 400, json.dumps({'error': 'backupData must be base64 endcoded'})
    except Exception:
        return 400, json.dumps({'error': 'backupData must be base64 endcoded'})

    await store(seed_hash, 'backup', backup_data.encode('utf-8'), self_hosted_config=self_hosted_config)

    return 200, json.dumps({'state': 'saved', 'backupData': backup_data})
