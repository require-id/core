import pytest

from app import router
from service.context import LambdaContext, LambdaEvent


class MockedRequest:
    def __init__(self, method='GET', path='/', headers=None, query=None, ip=None, host=None, read=None):
        self.method = method
        self.path = path
        self.headers = headers
        self.query = query
        self._cache = {'request_ip': ip}
        self.host = host
        self.read = read


@pytest.mark.asyncio
async def test_routing(loop):
    request = MockedRequest(path='/api/status')

    event = LambdaEvent(request)
    context = LambdaContext(request)

    response = await router.handler(await event.as_dict(), context, coro=True)
    status_code, body = response.get('statusCode'), response.get('body')
    assert status_code == 200
    assert body == '{"state": "online"}'
