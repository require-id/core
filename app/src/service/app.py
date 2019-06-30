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


class SelfHostedConfig:
    def __init__(self, config_data):
        self.aws_access_key_id = config_data.get('aws', {}).get('aws_access_key_id')
        self.aws_secret_access_key = config_data.get('aws', {}).get('aws_secret_access_key')

        self.backup_storage_method = config_data.get('backups', {}).get('storage_method')
        self.backup_s3_bucket = config_data.get('backups', {}).get('s3_bucket')


class Service(Base):
    name = 'require-id'

    def __init__(self):
        self.config = json.loads(os.getenv('CONFIG_DATA') or '{}')

    @tomodachi.http('*', r'/(?P<api>[^/]+?)/(?P<function_name>[^/]+?)/?')
    async def lambda_wrapper(self, request, api, function_name):
        api_key = request.headers.get('API-Key') or request.headers.get('X-API-Key')
        if api in ('app', 'backup') and api_key != self.config.get('api_key'):
            return 403, await self.error(403)

        if api != re.sub(r'[^a-z0-9_]', '', api) or function_name != re.sub(r'[^a-z0-9_]', '', function_name):
            return 404, await self.error(404)

        if not api or not function_name:
            return 404, await self.error(404)

        try:
            method_module = importlib.import_module(f'lambdas.index')
            func = getattr(method_module, 'handler', None)
        except ModuleNotFoundError:
            return 404, await self.error(404)

        if not func:
            return 404, await self.error(404)

        event = LambdaEvent(request)
        context = LambdaContext()
        self_hosted_config = SelfHostedConfig(self.config)

        status_code, body = await func(event.as_dict(), context, self_hosted_config=self_hosted_config)
        if status_code >= 400:
            return status_code, await self.error(status_code)
        return status_code, body
