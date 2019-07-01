import asyncio
import json
import os
import shutil

from app.shared.utils import async_call
from settings import settings

import botocore
try:
    import aiobotocore
except ImportError:
    import botocore.session

DATA_PATH = os.path.join(os.path.abspath(os.sep), 'app', 'data')


def _get_s3_client():
    try:
        session = aiobotocore.get_session(loop=asyncio.get_event_loop())
    except Exception:
        session = botocore.session.get_session()

    client = session.create_client(
        's3',
        region_name=settings.region,
        aws_secret_access_key=settings.aws_secret_access_key,
        aws_access_key_id=settings.aws_access_key_id,
        endpoint_url=settings.aws_s3_endpoint
    )

    return client


async def _delete_s3(file_type, identifier, delete_previous=False):
    client = _get_s3_client()
    key = f'{file_type}/{identifier}'

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
    file_path = os.path.join(DATA_PATH, file_type, identifier)

    if os.path.isfile(file_path):
        os.remove(file_path)

    if delete_previous:
        previousver_file_path = f'{file_path}.previousver'
        if os.path.isfile(previousver_file_path):
            os.remove(previousver_file_path)


async def _load_s3(file_type, identifier):
    client = _get_s3_client()

    try:
        object_data = await async_call(client.get_object(
            Bucket=settings.aws_s3_bucket,
            Key=f'{file_type}/{identifier}'
        ))
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return b''
        else:
            raise e

    return await async_call(object_data.get('Body').read())


async def _load_local(file_type, identifier):
    file_path = os.path.join(DATA_PATH, file_type, identifier)

    if os.path.isfile(file_path):
        with open(file_path, 'rb') as file:
            return file.read()

    return b''


async def _store_s3(file_type, identifier, data, save_previous=False):
    client = _get_s3_client()
    key = f'{file_type}/{identifier}'

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
            else:
                raise e

    await async_call(client.put_object(
        Bucket=settings.aws_s3_bucket,
        Key=key,
        Body=data
    ))


async def _store_local(file_type, identifier, data, save_previous=False):
    directory = os.path.join(DATA_PATH, file_type)
    file_path = os.path.join(directory, identifier)

    if isinstance(data, str):
        data = data.encode('utf-8')
    if not isinstance(data, bytes):
        data = json.dumps(data).encode()

    if not os.path.isdir(directory):
        os.makedirs(directory)

    if save_previous and os.path.isfile(file_path):
        shutil.copyfile(file_path, f'{file_path}.previousver')

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
