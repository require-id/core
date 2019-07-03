from app.shared import schema
from app.shared.data import load
from app.shared.handler import lambda_handler

SCHEMA = schema.Schema(
    seed_hash=schema.HASH | schema.REQUIRED
)


@lambda_handler(SCHEMA)
async def handler(values=None, **kwargs):
    backup_data = await load('backup', values.seed_hash, decode=False)

    if backup_data:
        return 200, {'state': 'saved', 'backupData': backup_data.decode('utf-8')}

    return 404, {'error': 'No such seedHash'}
