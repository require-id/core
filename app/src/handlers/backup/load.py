import asyncio
import json


async def handler(event, context):
    aws_request_id = context.aws_request_id
    method = event.get('httpMethod')

    if method not in ('HEAD', 'GET'):
        return {
            'statusCode': 405,
            'body': json.dumps({'message': 'Method Not Allowed'})
        }

    return {
        'statusCode': 200,
        'body': f'{method} – backup.load: {aws_request_id}'
    }


def run(event, context):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(handler(event, context))
