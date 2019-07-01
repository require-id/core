import asyncio
import os
import shutil

from app.shared.utils import async_call
from settings import settings

import botocore
try:
    import aiobotocore
except ImportError:
    pass

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


async def _delete_s3(identifier, file_type):
    bucket = settings.aws_s3_bucket
    key = f'{file_type}/{identifier}'

    client = _get_s3_client()

    await async_call(client.delete_object(
        Bucket=bucket,
        Key=key
    ))

    if file_type == 'backup':
        await async_call(client.delete_object(
            Bucket=bucket,
            Key=f'{key}.previousver'
        ))


async def _delete_local(identifier, file_type):
    file_path = os.path.join(DATA_PATH, file_type, identifier)

    if os.path.isfile(file_path):
        os.remove(file_path)

    if file_type == 'backup':
        previousver_file_path = f'{file_path}.previousver'
        if os.path.isfile(previousver_file_path):
            os.remove(previousver_file_path)


async def _load_s3(identifier, file_type):
    bucket = settings.aws_s3_bucket
    key = f'{file_type}/{identifier}'

    client = _get_s3_client()

    try:
        object_data = await async_call(client.get_object(
            Bucket=bucket,
            Key=key
        ))
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return b''
        else:
            raise e

    return await async_call(object_data.get('Body').read())


async def _load_local(identifier, file_type):
    file_path = os.path.join(DATA_PATH, file_type, identifier)

    if os.path.isfile(file_path):
        with open(file_path, 'rb') as backup_file:
            return backup_file.read()

    return b''


async def _store_s3(identifier, file_type, data):
    bucket = settings.aws_s3_bucket
    key = f'{file_type}/{identifier}'

    client = _get_s3_client()

    if file_type == 'backup':
        try:
            await async_call(client.copy_object(
                Bucket=bucket,
                Key=f'{key}.previousver',
                CopySource={'Bucket': bucket, 'Key': key}
            ))
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                pass
            else:
                raise e

    await async_call(client.put_object(
        Bucket=bucket,
        Key=key,
        Body=data
    ))


async def _store_local(identifier, file_type, data):
    directory = os.path.join(DATA_PATH, file_type)
    if not os.path.isdir(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, identifier)
    if file_type == 'backup' and os.path.isfile(file_path):
        shutil.copyfile(file_path, f'{file_path}.previousver')

    with open(file_path, 'wb') as backup_file:
        backup_file.write(data)


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
