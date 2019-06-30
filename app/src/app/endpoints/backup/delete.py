import json

from app.shared import data
from app.shared.utils import validate_hash


async def handler(event, context, self_hosted_config=None):
    aws_request_id = context.aws_request_id

    seed_hash = event.get('queryStringParameters', {}).get('seedHash')
    if not validate_hash(seed_hash):
        return 400, json.dumps({'error': 'Invalid value for seedHash'})

    await data.delete(seed_hash, 'backup', self_hosted_config)

    return 200, json.dumps({'request_id': aws_request_id, 'message': 'Backup data deleted.'})
