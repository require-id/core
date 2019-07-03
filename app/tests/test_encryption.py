import pytest

from app.shared.encryption import encrypt, decrypt


@pytest.mark.asyncio
async def test_encryption(loop):
    password = 'this-is-a-password'
    content = 'require.id content'

    encrypted_content = encrypt(content, password)
    assert encrypted_content != content

    assert decrypt(encrypted_content, password).decode('utf-8') == content
