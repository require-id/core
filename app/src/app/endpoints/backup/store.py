import json

from app.shared import data
from app.shared.utils import validate_base64, validate_hash


async def handler(event, context, self_hosted_config=None):
    aws_request_id = context.aws_request_id

    body = json.loads(event.get('body'))
    seed_hash = body.get('seedHash')

    if not validate_hash(seed_hash):
        return 400, json.dumps({'error': 'Invalid value for seedHash'})

    backup_data = body.get('data')
    if isinstance(backup_data, str):
        backup_data = backup_data.encode('utf-8')
    if not validate_base64(backup_data):
        return 400, json.dumps({'error': 'Data must be base64 endcoded.'})

    await data.store(seed_hash, 'backup', backup_data, self_hosted_config)

    return 200, json.dumps({'request_id': aws_request_id, 'message': 'Backup data stored.'})
