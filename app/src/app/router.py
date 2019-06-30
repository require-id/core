import asyncio
import importlib
import json
import re

from app.shared.exceptions import InvalidConfigError


async def handler(event, context, self_hosted_config=None):
    unknown_api_response = 404, json.dumps({'message': 'Invalid API'})

    path = event.get('path')
    try:
        _, api, function_name = path.split('/')
    except Exception:
        return unknown_api_response

    if api != re.sub(r'[^a-z0-9_]', '', api) or function_name != re.sub(r'[^a-z0-9_]', '', function_name):
        return unknown_api_response

    if not api or not function_name:
        return unknown_api_response

    method_module = None
    try:
        method_module = importlib.import_module(f'app.endpoints.{api}.{function_name}')
    except ModuleNotFoundError:
        raise
        return unknown_api_response

    func = getattr(method_module, 'handler', None)
    return await func(event, context)


def run(event, context):
    loop = asyncio.get_event_loop()
    try:
        status_code, body = loop.run_until_complete(handler(event, context))
#    except InvalidConfigError:
#        status_code = 500
#        body = json.dumps({'message': 'Invalid config.'})
    except Exception:
        raise
        status_code = 500
        body = json.dumps({'message': 'Internal Server Error'})

    return {
        'statusCode': status_code,
        'body': body
    }
