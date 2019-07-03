import hashlib
import pytest

from app.shared.validation import validate_base64, validate_hash, validate_timestamp, validate_url, validate_uuid


@pytest.mark.asyncio
async def test_timestamp_validation(loop):
    assert validate_timestamp('1984-08-01T22:30:20.004711Z')
    assert not validate_timestamp('1984-08-01')
    assert validate_timestamp('1984-08-01T23:00:00')
    assert not validate_timestamp('1984-08-01T24:00:00')


@pytest.mark.asyncio
async def test_base64_validation(loop):
    assert validate_base64(b'cmVxdWlyZS5pZA==')
    assert not validate_base64(b'invaliddata')


@pytest.mark.asyncio
async def test_hash_validation(loop):
    assert validate_hash(hashlib.sha3_256(b'test').hexdigest())
    assert validate_hash('c5b91387045b8dbfc26544855c3b7a5a21684485d39ac423aeb4552490f155e2')
    assert validate_hash('C5B91387045B8DBFC26544855C3B7A5A21684485D39AC423AEB4552490F155E2')
    assert validate_hash('0000000000000000000000000000000000000000000000000000000000000000')
    assert not validate_hash('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    assert not validate_hash('c5b91387045b8dbfc5b91387045b8dbf')
    assert not validate_hash('c5b91387045b8dbfc5b91387045b8dbfz5b91387045b8dbfc5b91387045b8dbf')
    assert not validate_hash('c5b91387045b8dbfc5b91387045b8dbf5b91387045b8dbfc5b91387045b8dbf')


@pytest.mark.asyncio
async def test_url_validation(loop):
    assert validate_url('https://api.require.id/api/status')
    assert validate_url('https://api.require.id')
    assert validate_url('https://document.now')
    assert validate_url('https://fictionalphotographer.photography/webhook')
    assert validate_url('http://example.org:4711/path')
    assert validate_url('http://example.com/?key=value&anotherKey=anotherValue')
    assert validate_url('http://1.1.1.1/')
    assert validate_url('https://open.spotify.com/playlist/3KrZnBrru7Z3l36a0ml255?si=HC7Yfvs3QRi8x6_LFY7rsQ')
    assert not validate_url('ftp://example.org/')
    assert not validate_url('spotify:playlist:3KrZnBrru7Z3l36a0ml255')


@pytest.mark.asyncio
async def test_uuid_validation(loop):
    assert validate_uuid('d4d15151-5d20-45f9-a4f6-b99943b4c470')
    assert not validate_uuid('xxxxxxxx-5d20-45f9-a4f6-b99943b4c470')
    assert not validate_uuid('d4d151515d2045f9a4f6b99943b4c470')
