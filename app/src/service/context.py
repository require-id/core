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
            'body': await self.read_body(),
            'isBase64Encoded': False
        }
