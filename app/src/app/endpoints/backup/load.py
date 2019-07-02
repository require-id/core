from app.shared import schema
from app.shared.data import load

SCHEMA = schema.Schema(
    seed_hash=schema.HASH | schema.REQUIRED
)


async def handler(event, context):
    values = await SCHEMA.load(event.get('queryStringParameters', {}))
    if values.error:
        return 400, {'error': values.error}

    backup_data = await load('backup', values.seed_hash, decode=False)

    if backup_data:
        return 200, {'state': 'saved', 'backupData': backup_data.decode('utf-8')}

    return 404, {'error': 'No such seedHash'}
