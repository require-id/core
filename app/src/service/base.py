import json
import os

import tomodachi


class Base(tomodachi.Service):
    error_responses = {
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Missing Authentication Token',
        405: 'Method Not Allowed',
        406: 'Not Acceptable',
        411: 'Length required',
        413: 'Request Entity Too Large',
        414: 'Request URI Too Long',
        431: 'Request Header Too Large',
        500: 'Internal Server Error'
    }

    options = {
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
        return json.dumps({'message': self.error_responses.get(status_code, 'unknown')})

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
