from app.shared import schema
from app.shared.data import delete
from app.shared.handler import lambda_handler

SCHEMA = schema.Schema(
    seed_hash=schema.HASH | schema.REQUIRED
)


@lambda_handler(SCHEMA)
async def handler(values=None, **kwargs):
    await delete('backup', values.seed_hash, delete_previous=True)

    return 200, {'state': 'deleted'}
