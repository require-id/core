import asyncio

import pytest


@pytest.yield_fixture(scope='module')
def loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    yield loop

    try:
        if loop and not loop.is_closed():
            loop.close()
    except RuntimeWarning:
        pass
