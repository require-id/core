import re
import importlib

import tomodachi

from handlers.load import handler as load_handler
from service.base import Base


class Service(Base):
    name = 'require-id'

    @tomodachi.http('*', r'/(?P<function_name>[^/]+?)/?')
    async def lambda_wrapper(self, request, function_name):
        function_name = re.sub(r'[^a-z0-9_]', '_', function_name)
        try:
            method_module = importlib.import_module(f'handlers.{function_name}')
            func = getattr(method_module, 'handler', None)
        except ModuleNotFoundError:
            return 404, await self.error(404)

        if not func:
            return 404, await self.error(404)

        response = await func(None, None)
        return response.get('statusCode'), response.get('body')
