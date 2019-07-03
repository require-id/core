import tomodachi

from app import router
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
