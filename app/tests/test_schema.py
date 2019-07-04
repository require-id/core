import base64
import datetime

import pytest

from app.shared import schema


@pytest.mark.asyncio
async def test_schema(loop):
    SCHEMA = schema.Schema(
        prompt_user_hash=schema.HASH | schema.REQUIRED,
        timestamp=(schema.TIMESTAMP, lambda: datetime.datetime.utcnow()),
        expire=(schema.EXPIRE, 90),
        encrypted_data=schema.BASE64
    )

    values = await SCHEMA.load('''{
        "promptUserHash": "ebd25cfe070ab282250533a201e38c83249d489a3bf1c8f9718bad6369f59994",
        "encryptedData": "dGVzdA=="
    }''')

    assert not values.error
    assert values.prompt_user_hash == 'ebd25cfe070ab282250533a201e38c83249d489a3bf1c8f9718bad6369f59994'
    assert isinstance(values.timestamp, datetime.datetime)
    assert values.expire == 90
    assert base64.b64decode(values.encrypted_data.encode('utf-8')).decode() == 'test'


@pytest.mark.asyncio
async def test_missing_value(loop):
    SCHEMA = schema.Schema(
        required_value=schema.REQUIRED
    )

    values = await SCHEMA.load('''{}''')

    assert values.error == 'Missing required input: requiredValue'


@pytest.mark.asyncio
async def test_unknown_value(loop):
    SCHEMA = schema.Schema(
        required_value=schema.REQUIRED
    )

    values = await SCHEMA.load('''{
        "requiredValue": "required value",
        "anotherValue": "should not be set"
    }''')

    assert values.error == 'Unknown input: anotherValue'
