from app.shared import schema
from app.shared.data import delete

SCHEMA = schema.Schema(
    seed_hash=schema.HASH | schema.REQUIRED
)


async def handler(event, context):
    values = await SCHEMA.load(event.get('queryStringParameters', {}))
    if values.error:
        return 400, {'error': values.error}

    await delete('backup', values.seed_hash, delete_previous=True)

    return 200, {'state': 'deleted'}
