import json
from app.shared import data


async def handler(event, context, self_hosted_config=None):
    aws_request_id = context.aws_request_id

    body = json.loads(event.get('body'))
    seed_hash = body.get('seedHash')
    backup_data = body.get('data')
    if isinstance(backup_data, str):
        backup_data = backup_data.encode('utf-8')

    await data.store(seed_hash, self_hosted_config, file_type='backup', data=backup_data)

    return 200, f'backup.store: {aws_request_id}'
