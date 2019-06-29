import asyncio


async def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'This is the load function'
    }


def run(event, context):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(handler(event, context))
