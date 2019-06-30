import asyncio
import importlib
import json
import re


async def handler(event, context, self_hosted_config=None):
    unknown_api_response = 404, json.dumps({'message': 'Invalid API'})

    path = event.get('path')
    try:
        _, api, function_name = path.split('/')
    except Exception:
        return unknown_api_response

    if api != re.sub(r'[^a-z0-9_]', '', api) or function_name != re.sub(r'[^a-z0-9_]', '', function_name):
        return 404, await self.error(404)

    if not api or not function_name:
        return unknown_api_response

    method_module = None
    try:
        method_module = importlib.import_module(f'api.{api}.{function_name}')
    except ModuleNotFoundError:
        try:
            method_module = importlib.import_module(f'lambdas.api.{api}.{function_name}')
        except ModuleNotFoundError:
            return unknown_api_response

    func = getattr(method_module, 'handler', None)
    return await func(event, context)

def run(event, context):
    loop = asyncio.get_event_loop()
    status_code, body = loop.run_until_complete(handler(event, context))

    return {
        'statusCode': status_code,
        'body': body
    }
