import asyncio
import json
import os
import shutil
from typing import Awaitable

import botocore

try:
    import aiobotocore
except ImportError:
    pass

BUCKETS = json.loads(os.getenv('BUCKETS', '{}'))
DATA_PATH = os.path.join(os.path.abspath(os.sep), 'app', 'data')


async def router(identifier, self_hosted_config, file_type, s3_function, docker_volume_function, data=None):
    '''
    This function should probably be named soemthing better.
    '''

    if not self_hosted_config or self_hosted_config.storage_method == 's3':
        return await s3_function(identifier, file_type, self_hosted_config=self_hosted_config, data=data)
    else:
        return docker_volume_function(identifier, file_type, data=data)


def _s3_client(self_hosted_config):
    try:
        session = aiobotocore.get_session(loop=asyncio.get_event_loop())
        client = session.create_client(
            's3',
            region_name='us-west-1',
            aws_secret_access_key=self_hosted_config.aws_secret_access_key,
            aws_access_key_id=self_hosted_config.aws_access_key_id,
            endpoint=self_hosted_config.aws_s3_endpoint
        )
    except Exception:
        session = botocore.session.get_session()
        client = session.create_client('s3')

    return client


async def delete(identifier, file_type, self_hosted_config):
    await router(
        identifier,
        self_hosted_config,
        file_type=file_type,
        s3_function=_delete_s3,
        docker_volume_function=_delete_local
    )


async def _delete_s3(identifier, file_type, self_hosted_config, **kwargs):
    bucket = BUCKETS.get(file_type)
    key = f'{file_type}/{identifier}'

    client = _s3_client(self_hosted_config)
    versions = client.list_object_versions(Bucket=bucket, Prefix=key)
    if isinstance(versions, Awaitable):
        versions = await versions

    for object_version in versions.get('Versions'):
        delete_function = client.delete_object(
            Bucket=bucket,
            Key=key,
            VersionId=object_version.get('VersionId')
        )
        if isinstance(delete_function, Awaitable):
            await delete_function


def _delete_local(identifier, file_type, **kwargs):
    file_path = os.path.join(DATA_PATH, file_type, identifier)
    if os.path.isfile(file_path):
        os.remove(file_path)

    if not file_type == 'backup':
        return
    previousver_file_path = f'{file_path}.previousver'
    if os.path.isfile(previousver_file_path):
        os.remove(previousver_file_path)


async def load(identifier, file_type, self_hosted_config):
    return await router(
        identifier,
        self_hosted_config,
        file_type=file_type,
        s3_function=_load_s3,
        docker_volume_function=_load_local
    )


async def _load_s3(identifier, file_type, self_hosted_config, **kwargs):
    client = _s3_client(self_hosted_config)
    object_data = client.get_object(
        Bucket=BUCKETS.get(file_type),
        Key=f'{file_type}/{identifier}'
    )
    if isinstance(object_data, Awaitable):
        object_data = await object_data
    return object_data.get('Body')


def _load_local(identifier, file_type, **kwargs):
    file_path = os.path.join(DATA_PATH, file_type, identifier)
    if os.path.isfile(file_path):
        with open(file_path) as backup_file:
            return backup_file.read()


async def store(identifier, file_type, data, self_hosted_config):
    await router(
        identifier,
        self_hosted_config,
        file_type=file_type,
        s3_function=_store_s3,
        docker_volume_function=_store_local,
        data=data
    )


async def _store_s3(identifier, file_type, self_hosted_config, data, **kwargs):
    client = _s3_client(self_hosted_config)
    put_object = client.put_object(
        Bucket=BUCKETS.get(file_type),
        Key=f'{file_type}/{identifier}',
        Body=data
    )
    if isinstance(put_object, Awaitable):
        await put_object


def _store_local(identifier, file_type, data, **kwargs):
    file_path = os.path.join(DATA_PATH, file_type, identifier)
    if os.path.isfile(file_path):
        shutil.copyfile(file_path, f'{file_path}.previousver')

    with open(file_path, 'wb') as backup_file:
        backup_file.write(data)
