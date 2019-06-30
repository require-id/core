import asyncio
import json


async def handler(event, context):
    aws_request_id = context.aws_request_id
    body = json.loads(event.get('body'))

    return 200, f'app.response: {aws_request_id}'
