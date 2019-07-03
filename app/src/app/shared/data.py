import asyncio
import json
import os
import shutil

import botocore
try:
    import aiobotocore
except ImportError:
    import botocore.session

from app.shared.encryption import encrypt, decrypt
from app.shared.utils import async_call, sha3
from settings import settings

DATA_PATH = os.path.join(os.path.abspath(os.sep), 'app', 'data')


def _get_s3_client():
    try:
        session = aiobotocore.get_session(loop=asyncio.get_event_loop())
    except Exception:
        session = botocore.session.get_session()

    kwargs = {k: v for k, v in {
        'region_name': settings.aws_region,
        'aws_access_key_id': settings.aws_access_key_id,
        'aws_secret_access_key': settings.aws_secret_access_key,
        'endpoint_url': settings.aws_s3_endpoint
    }.items() if v is not None}

    return session.create_client('s3', **kwargs)


async def _delete_s3(file_type, identifier, delete_previous=False):
    client = _get_s3_client()
    key = '{}/{}'.format(file_type, sha3(identifier))

    await async_call(client.delete_object(
        Bucket=settings.aws_s3_bucket,
        Key=key
    ))

    if delete_previous:
        await async_call(client.delete_object(
            Bucket=settings.aws_s3_bucket,
            Key=f'{key}.previousver'
        ))


async def _delete_local(file_type, identifier, delete_previous=False):
    file_path = os.path.join(DATA_PATH, file_type, sha3(identifier))

    if os.path.isfile(file_path):
        os.remove(file_path)

    if delete_previous:
        previousver_file_path = f'{file_path}.previousver'
        if os.path.isfile(previousver_file_path):
            os.remove(previousver_file_path)


async def _load_s3(file_type, identifier, decode=True):
    client = _get_s3_client()

    try:
        object_data = await async_call(client.get_object(
            Bucket=settings.aws_s3_bucket,
            Key='{}/{}'.format(file_type, sha3(identifier))
        ))
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return None
        if e.response['Error']['Code'] == 'AccessDenied':
            return None
        else:
            raise e

    data = await async_call(object_data.get('Body').read())

    if data:
        data = decrypt(data, identifier)

    try:
        if data and decode:
            return json.loads(data)
    except Exception:
        pass

    return data


async def _load_local(file_type, identifier, decode=True):
    file_path = os.path.join(DATA_PATH, file_type, sha3(identifier))

    if os.path.isfile(file_path):
        with open(file_path, 'rb') as file:
            data = file.read()

            if data:
                data = decrypt(data, identifier)

            try:
                if data and decode:
                    return json.loads(data)
            except Exception:
                pass

            return data

    return None


async def _store_s3(file_type, identifier, data, save_previous=False):
    client = _get_s3_client()
    key = '{}/{}'.format(file_type, sha3(identifier))

    if isinstance(data, str):
        data = data.encode('utf-8')
    if not isinstance(data, bytes):
        data = json.dumps(data).encode()

    if save_previous:
        try:
            await async_call(client.copy_object(
                Bucket=settings.aws_s3_bucket,
                Key=f'{key}.previousver',
                CopySource={'Bucket': settings.aws_s3_bucket, 'Key': key}
            ))
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                pass
            if e.response['Error']['Code'] == 'AccessDenied':
                pass
            else:
                raise e

    if data:
        data = encrypt(data, identifier)

    await async_call(client.put_object(
        Bucket=settings.aws_s3_bucket,
        Key=key,
        Body=data
    ))


async def _store_local(file_type, identifier, data, save_previous=False):
    directory = os.path.join(DATA_PATH, file_type)
    file_path = os.path.join(directory, sha3(identifier))

    if isinstance(data, str):
        data = data.encode('utf-8')
    if not isinstance(data, bytes):
        data = json.dumps(data).encode()

    if not os.path.isdir(directory):
        os.makedirs(directory)

    if save_previous and os.path.isfile(file_path):
        shutil.copyfile(file_path, f'{file_path}.previousver')

    if data:
        data = encrypt(data, identifier)

    with open(file_path, 'wb') as file:
        file.write(data)


delete_functions = {
    's3': _delete_s3,
    'docker_volume': _delete_local
}
load_functions = {
    's3': _load_s3,
    'docker_volume': _load_local
}
store_functions = {
    's3': _store_s3,
    'docker_volume': _store_local
}

delete = delete_functions.get(settings.storage_method)
load = load_functions.get(settings.storage_method)
store = store_functions.get(settings.storage_method)
