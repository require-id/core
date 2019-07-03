from app.shared import schema
from app.shared.data import store
from app.shared.handler import lambda_handler

SCHEMA = schema.Schema(
    seed_hash=schema.HASH | schema.REQUIRED,
    backup_data=schema.BASE64 | schema.REQUIRED
)


@lambda_handler(SCHEMA)
async def handler(values=None, **kwargs):
    await store('backup', values.seed_hash, values.backup_data, save_previous=True)

    return 200, {
        'state': 'saved',
        'backupData': values.backup_data
    }
