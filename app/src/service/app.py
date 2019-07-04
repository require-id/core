import datetime
import os

import tomodachi

from app import router
from app.shared.data import mtime, DATA_PATH
from settings import settings
from service.base import Base
from service.context import LambdaContext, LambdaEvent


class Service(Base):
    name = 'require-id'
    routes = {
        ('api', 'status'): ('GET', settings.app_api_key),
        ('user', 'poll'): ('GET', settings.app_api_key),
        ('user', 'response'): ('POST', settings.app_api_key),
        ('user', 'subscribe'): ('POST', settings.app_api_key),
        ('user', 'unsubscribe'): ('POST', settings.app_api_key),
        ('backup', 'store'): ('POST', settings.app_api_key),
        ('backup', 'load'): ('GET', settings.app_api_key),
        ('backup', 'delete'): ('DELETE', settings.app_api_key),
        ('prompt', 'new'): ('POST', settings.prompt_api_key),
        ('prompt', 'poll'): ('GET', settings.prompt_api_key),
        ('prompt', 'abort'): ('DELETE', settings.prompt_api_key)
    }

    def __init__(self):
        if not settings.storage_method:
            raise Exception('Invalid storage_method')

    @tomodachi.http('*', r'/(?P<api>[^/]+?)/(?P<function_name>[^/]+?)/?')
    async def lambda_wrapper(self, request, api, function_name):
        route = (api, function_name)
        if route not in self.routes:
            return 404, await self.error(404)

        allowed_method, expected_api_key = self.routes[route]
        request_method = request.method
        if request_method == 'HEAD':
            request_method = 'GET'

        if expected_api_key and request.headers.get('X-API-Key') != expected_api_key:
            return 403, await self.error(403)

        if allowed_method not in ('ANY', '*') and allowed_method != request.method:
            return 404, await self.error(404)

        event = LambdaEvent(request)
        context = LambdaContext(request)

        response = await router.handler(await event.as_dict(), context, coro=True)
        status_code, body = response.get('statusCode'), response.get('body')

        return status_code, body

    @tomodachi.schedule('minutely', immediately=True)
    async def clean_data_files(self):
        expire = datetime.datetime.utcnow() - datetime.timedelta(seconds=3600)
        file_types = ('user', 'prompt')
        if settings.storage_method == 'docker_volume':
            for file_type in file_types:
                for root, dirs, files in os.walk(os.path.join(DATA_PATH, file_type), topdown=True):
                    for file in files:
                        file_path = os.path.join(root, file)
                        _file_type, filename = file_path.rsplit(os.sep)[-2:]
                        if _file_type == file_type:
                            ts = await mtime(file_type, filename)
                            if ts < expire:
                                os.remove(file_path)
