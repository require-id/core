import asyncio
import json


async def handler(event, context):
    aws_request_id = context.aws_request_id

    return 200, f'app.poll: {aws_request_id}'
