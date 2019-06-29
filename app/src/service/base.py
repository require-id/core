import json
import os

import tomodachi


class Base(tomodachi.Service):
    error_responses = {
        400: 'bad-request',
        401: 'unauthorized',
        403: 'forbidden',
        404: 'not-found',
        405: 'method-not-allowed',
        406: 'not-acceptable',
        411: 'length-required',
        413: 'request-entity-too-large',
        414: 'request-uri-too-long',
        431: 'request-header-too-large',
        500: 'internal-server-error'
    }

    def __init__(self) -> None:
        # Default options
        self.options = {
            'http': {
                'port': 8080,
                'content_type': 'application/json; charset=utf-8',
                'access_log': True,
                'real_ip_from': '127.0.0.1'
            }
        }

    @tomodachi.http('GET', r'/health/?')
    async def health(self, request):
        return await json.dumps({'status': 'ok'})

    async def error(self, status_code):
        return json.dumps({'error': self.error_responses.get(status_code, 'unknown')})

    @tomodachi.http_error(status_code=400)
    async def error_400(self, request):
        return await self.error(400)

    @tomodachi.http_error(status_code=401)
    async def error_401(self, request):
        return await self.error(401)

    @tomodachi.http_error(status_code=403)
    async def error_403(self, request):
        return await self.error(403)

    @tomodachi.http_error(status_code=404)
    async def error_404(self, request):
        return await self.error(404)

    @tomodachi.http_error(status_code=405)
    async def error_405(self, request):
        return await self.error(405)

    @tomodachi.http_error(status_code=406)
    async def error_406(self, request):
        return await self.error(406)

    @tomodachi.http_error(status_code=411)
    async def error_411(self, request):
        return await self.error(411)

    @tomodachi.http_error(status_code=413)
    async def error_413(self, request):
        return await self.error(413)

    @tomodachi.http_error(status_code=414)
    async def error_414(self, request):
        return await self.error(414)

    @tomodachi.http_error(status_code=431)
    async def error_431(self, request):
        return await self.error(431)

    @tomodachi.http_error(status_code=500)
    async def error_500(self, request):
        return await self.error(500)
