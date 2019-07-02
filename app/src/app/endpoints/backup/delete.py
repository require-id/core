from app.shared.data import delete
from app.shared.utils import get_query_value, validate_hash


async def handler(event, context):
    seed_hash = get_query_value(event, ('seedHash', 'hash'), '').lower()

    if not validate_hash(seed_hash):
        return 400, {'error': 'Invalid value for seedHash'}

    await delete('backup', seed_hash, delete_previous=True)

    return 200, {'state': 'deleted'}
