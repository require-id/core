import importlib
import json
import os
import re
import uuid

import tomodachi

from service.base import Base


class LambdaContext:
    def __init__(self):
        self.aws_request_id = str(uuid.uuid4())


class LambdaEvent:
    def __init__(self, request):
        self.method = request.method
        self.path = request.path
        self.headers = request.headers

    def as_dict(self):
        return {
            'resource': self.path,
            'path': self.path,
            'httpMethod': self.method,
            'headers': dict(self.headers),
            'multiValueHeaders': {k: [v] for k, v in self.headers.items()},
            'queryStringParameters': None,
            'multiValueQueryStringParameters': None,
            'pathParameters': None,
            'stageVariables': None,
            'requestContext': {

            },
            'body': None,
            'isBase64Encoded': False
        }


class Service(Base):
    name = 'require-id'

    def __init__(self):
        config_data = json.loads(os.getenv('CONFIG_DATA') or '{}')
        self.api_key = config_data.get('api_key')

    @tomodachi.http('*', r'/(?P<api>[^/]+?)/?(?P<function_name>[^/]+?)/?')
    async def lambda_wrapper(self, request, api, function_name):
        api_key = request.headers.get('API-Key') or request.headers.get('X-API-Key')
        if api_key != self.api_key:
            return 403, await self.error(403)

        api = re.sub(r'[^a-z0-9_]', '_', api)
        function_name = re.sub(r'[^a-z0-9_]', '_', function_name)

        if not api or not function_name:
            return 404, await self.error(404)

        try:
            method_module = importlib.import_module(f'handlers.{api}.{function_name}')
            func = getattr(method_module, 'handler', None)
        except ModuleNotFoundError:
            return 404, await self.error(404)

        if not func:
            return 404, await self.error(404)

        event = LambdaEvent(request)
        context = LambdaContext()

        response = await func(event.as_dict(), context)
        status_code = response.get('statusCode')
        if status_code >= 400:
            return status_code, await self.error(status_code)
        return status_code, response.get('body')
