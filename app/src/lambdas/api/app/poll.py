import asyncio
import json


async def handler(event, context):
    aws_request_id = context.aws_request_id
    method = event.get('httpMethod')

    if method not in ('HEAD', 'GET'):
        return 405, 'Method Not Allowed'

    return {
        'statusCode': 200,
        'body': f'{method} – app.poll: {aws_request_id}'
    }
