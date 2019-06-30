import asyncio
import json
import app.router

async def handler(event, context):
    return 200, json.dumps({'message': 'API accessible'})
