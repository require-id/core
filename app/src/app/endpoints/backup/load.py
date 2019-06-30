import json
from app.shared import data


async def handler(event, context, self_hosted_config=None):
    aws_request_id = context.aws_request_id

    seed_hash = event.get('queryStringParameters', {}).get('seedHash')
    backup_data = await data.load(seed_hash, self_hosted_config, file_type='backup')

    return 200, json.dumps({'request_id': aws_request_id, 'backup_data': backup_data})
