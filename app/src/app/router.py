import asyncio
import importlib
import json
import re
from settings import settings


async def handler(event, context):
    unknown_api_response = 404, json.dumps({'message': 'Invalid API'})

    path = event.get('path')
    try:
        _, api, function_name = path.split('/')
    except Exception:
        return unknown_api_response

    if api != re.sub(r'[^a-z0-9]', '', api) or function_name != re.sub(r'[^a-z0-9]', '', function_name):
        return unknown_api_response

    if not api or not function_name:
        return unknown_api_response

    method_module = None
    try:
        method_module = importlib.import_module(f'app.endpoints.{api}.{function_name}')
    except ModuleNotFoundError:
        return unknown_api_response

    func = getattr(method_module, 'handler', None)
    status_code, return_value = await func(event, context)

    if isinstance(return_value, dict) or isinstance(return_value, list):
        return_value = json.dumps(return_value)

    return status_code, return_value


def run(event, context):
    loop = asyncio.get_event_loop()
    try:
        status_code, body = loop.run_until_complete(handler(event, context))
    except Exception as e:
        status_code = 500
        body = json.dumps({'message': 'Internal server error'})
        if settings.debug:
            body = json.dumps({'message': 'Internal server error', 'error': str(e)})

    return {
        'statusCode': status_code,
        'body': body
    }
