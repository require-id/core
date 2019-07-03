import uuid


class LambdaContext:
    def __init__(self, request):
        self.aws_request_id = str(uuid.uuid4())


class LambdaEvent:
    def __init__(self, request):
        self.method = request.method
        self.path = request.path
        self.headers = request.headers
        self.query = request.query
        self.ip = request._cache.get('request_ip')
        self.host = request.host
        self.read_body = request.read

    async def as_dict(self):
        return {
            'resource': self.path,
            'path': self.path,
            'httpMethod': self.method,
            'headers': dict(self.headers) if self.headers else {},
            'multiValueHeaders': {k: [v] for k, v in self.headers.items()} if self.headers else {},
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
                    'apiKey': self.headers.get('X-API-Key') if self.headers else None,
                    'userAgent': self.headers.get('User-Agent') if self.headers else None,
                    'sourceIp': self.ip
                },
                'domainName': self.host
            },
            'body': await self.read_body() if self.read_body else None,
            'isBase64Encoded': False
        }
