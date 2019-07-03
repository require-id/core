import importlib
import json
import re

from app.shared.handler import lambda_handler


@lambda_handler
async def handler(event=None, context=None, **kwargs):
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

    return await func(event, context, coro=True)
