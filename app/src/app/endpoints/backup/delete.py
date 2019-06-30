from app.shared import data


async def handler(event, context, self_hosted_config=None):
    aws_request_id = context.aws_request_id

    seed_hash = event.get('queryStringParameters', {}).get('seedHash')
    await data.delete(seed_hash, self_hosted_config, file_type='backup')

    return 200, f'backup.delete: {aws_request_id}'
