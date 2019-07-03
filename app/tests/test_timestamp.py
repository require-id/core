import datetime

import pytest

from app.shared.utils import convert_timestamp


@pytest.mark.asyncio
async def test_timestamp(loop):
    assert convert_timestamp('1984-08-01T22:30:20.004711Z') == datetime.datetime(1984, 8, 1, 22, 30, 20, 4711)
    assert convert_timestamp('2019-02-28 10:22:30') == datetime.datetime(2019, 2, 28, 10, 22, 30, 0)
    assert convert_timestamp('2016-01-01 00:00:01 UTC') == datetime.datetime(2016, 1, 1, 0, 0, 1, 0)
    assert convert_timestamp('2016-01-01 00:00:01 CEST') is None
    assert convert_timestamp('2016-02-29T00:00:00.100000Z') == datetime.datetime(2016, 2, 29, 0, 0, 0, 100000)
    assert convert_timestamp('2016-02-29T00:00:00Z') == datetime.datetime(2016, 2, 29, 0, 0, 0, 0)
    assert convert_timestamp('2017-02-29T00:00:00.000000Z') is None
