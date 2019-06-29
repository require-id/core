import json


async def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'This is the load function'
    }
