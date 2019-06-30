import asyncio
import json


async def handler(event, context):
    aws_request_id = context.aws_request_id
    method = event.get('httpMethod')

    if method not in ('HEAD', 'GET'):
        return 405, json.dumps({'message': 'Method Not Allowed'})

    return 200, f'{method} – app.status: {aws_request_id}'
