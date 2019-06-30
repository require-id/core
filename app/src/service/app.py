import json
import os
import uuid

import tomodachi

from service.base import Base
from app import router


class LambdaContext:
    def __init__(self):
        self.aws_request_id = str(uuid.uuid4())


class LambdaEvent:
    def __init__(self, request):
        self.method = request.method
        self.path = request.path
        self.headers = request.headers
        self.query = request.query
        self.ip = request._cache.get('request_ip')
        self.host = request.host

    def as_dict(self):
        return {
            'resource': self.path,
            'path': self.path,
            'httpMethod': self.method,
            'headers': dict(self.headers),
            'multiValueHeaders': {k: [v] for k, v in self.headers.items()},
            'queryStringParameters': {k: v for k, v in self.query.items()} if self.query else None,
            'multiValueQueryStringParameters': {k: [v] for k, v in self.query.items()} if self.query else None,
            'pathParameters': None,
            'stageVariables': None,
            'requestContext': {
                'resourcePath': self.path,
                'httpMethod': self.method,
                'path': self.path,
                'protocol': 'HTTP/1.1',
                'identity': {
                    'apiKey': self.headers.get('X-API-Key'),
                    'userAgent': self.headers.get('User-Agent'),
                    'sourceIp': self.ip
                },
                'domainName': self.host
            },
            'body': None,
            'isBase64Encoded': False
        }


class SelfHostedConfig:
    def __init__(self, config_data):
        self.aws_access_key_id = config_data.get('aws', {}).get('aws_access_key_id')
        self.aws_secret_access_key = config_data.get('aws', {}).get('aws_secret_access_key')
        self.aws_s3_endpoint = config_data.get('endpoints', {}).get('s3')
        self.storage_method = config_data.get('storage_method')


class Service(Base):
    name = 'require-id'
    routes = {
        ('api', 'status'): ('GET', True),
        ('user', 'poll'): ('GET', True),
        ('user', 'response'): ('POST', True),
        ('user', 'subscribe'): ('POST', True),
        ('backup', 'store'): ('POST', True),
        ('backup', 'load'): ('GET', True),
        ('backup', 'delete'): ('DELETE', True),
        ('prompt', 'new'): ('POST', False),
        ('prompt', 'poll'): ('GET', False),
        ('prompt', 'abort'): ('DELETE', False)
    }

    def __init__(self):
        self.config = json.loads(os.getenv('CONFIG_DATA') or '{}')

    @tomodachi.http('*', r'/(?P<api>[^/]+?)/(?P<function_name>[^/]+?)/?')
    async def lambda_wrapper(self, request, api, function_name):
        route = (api, function_name)
        if route not in self.routes:
            return 404, await self.error(404)

        allowed_method, api_key_required = self.routes[route]
        request_method = request.method
        if request_method == 'HEAD':
            request_method = 'GET'

        if api_key_required and request.headers.get('X-API-Key') != self.config.get('api_key'):
            return 403, await self.error(403)

        if allowed_method not in ('ANY', '*') and allowed_method != request.method:
            return 404, await self.error(404)

        event = LambdaEvent(request)
        context = LambdaContext()
        self_hosted_config = SelfHostedConfig(self.config)

        status_code, body = await router.handler(event.as_dict(), context, self_hosted_config=self_hosted_config)
        if status_code >= 400:
            return status_code, await self.error(status_code)
        return status_code, body
