import asyncio
import json


async def handler(event, context):
    aws_request_id = context.aws_request_id
    body = event.get('body')

    return 200, f'prompt.abort: {aws_request_id}'
