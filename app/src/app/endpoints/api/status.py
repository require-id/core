import json


async def handler(event, context):
    return 200, json.dumps({'state': 'online'})
