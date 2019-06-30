import json

from app.shared import data
from app.shared.utils import validate_hash


async def handler(event, context, self_hosted_config=None):
    aws_request_id = context.aws_request_id

    query_string_parameters = event.get('queryStringParameters') or {}
    seed_hash = query_string_parameters.get('seedHash')
    if not seed_hash or not validate_hash(seed_hash):
        return 400, json.dumps({'error': 'Invalid value for seedHash'})

    backup_data = await data.load(seed_hash, 'backup', self_hosted_config)
    backup_data_content = await backup_data.read()
    if backup_data:
        return 200, json.dumps({'request_id': aws_request_id, 'backup_data': backup_data_content.decode()})

    return 404, json.dumps({'request_id': aws_request_id, 'message': 'No backup data found.'})
