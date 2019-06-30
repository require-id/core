import asyncio
import json


async def handler(event, context):
    aws_request_id = context.aws_request_id
    method = event.get('httpMethod')
    body = event.get('body')

    if method not in ('POST', ):
        return 405, json.dumps({'message': 'Method Not Allowed'})

    return 200, f'{method} – prompt.new: {aws_request_id}'
