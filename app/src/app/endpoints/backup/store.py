import json

from app.shared import schema
from app.shared.data import store

SCHEMA = schema.Schema(
    seed_hash=schema.HASH | schema.REQUIRED,
    backup_data=schema.BASE64 | schema.REQUIRED
)


async def handler(event, context):
    values = await SCHEMA.load(event.get('body'))
    if values.error:
        return 400, {'error': values.error}

    await store('backup', values.seed_hash, values.backup_data, save_previous=True)

    return 200, {
        'state': 'saved',
        'backupData': values.backup_data
    }
