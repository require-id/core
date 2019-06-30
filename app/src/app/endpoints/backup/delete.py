from shared import data


async def handler(event, context, self_hosted_config=None):
    aws_request_id = context.aws_request_id

    await data.delete(event, context, self_hosted_config, file_type='backup')

    return 200, f'backup.delete: {aws_request_id}'
