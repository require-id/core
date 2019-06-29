import asyncio


async def handler(event, context):
    aws_request_id = context.aws_request_id
    method = event.get('httpMethod')

    return {
        'statusCode': 200,
        'body': f'{method} – store: {aws_request_id}'
    }


def run(event, context):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(handler(event, context))
