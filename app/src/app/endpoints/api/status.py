import asyncio
import json
import app.router

async def handler(event, context, self_hosted_config=None):
    return 200, json.dumps({'message': 'API accessible'})
