import asyncio
import json


async def handler(event, context):
    return 200, json.dumps({'ok': 'API accessible'})
