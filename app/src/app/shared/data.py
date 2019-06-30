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

BUCKETS = json.loads(os.getenv('BUCKETS', '{"backup":"require-id"}'))
DATA_PATH = os.path.join(os.path.abspath(os.sep), 'app', 'data')


async def router(identifier, file_type, self_hosted_config, s3_function, docker_volume_function, data=None):
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
            region_name='eu-west-1',
            aws_secret_access_key=self_hosted_config.aws_secret_access_key,
            aws_access_key_id=self_hosted_config.aws_access_key_id,
            endpoint_url=self_hosted_config.aws_s3_endpoint
        )
    except Exception:
        session = botocore.session.get_session()
        client = session.create_client('s3')

    return client


async def delete(identifier, file_type, self_hosted_config=None):
    await router(
        identifier,
        file_type=file_type,
        self_hosted_config=self_hosted_config,
        s3_function=_delete_s3,
        docker_volume_function=_delete_local
    )


async def _delete_s3(identifier, file_type, self_hosted_config, **kwargs):
    bucket = BUCKETS.get(file_type)
    key = f'{file_type}/{identifier}'

    client = _s3_client(self_hosted_config)

    delete_function = client.delete_object(
        Bucket=bucket,
        Key=key
    )
    if isinstance(delete_function, Awaitable):
        await delete_function

    if file_type == 'backup':
        delete_function = client.delete_object(
            Bucket=bucket,
            Key=f'{key}.previousver'
        )
        if isinstance(delete_function, Awaitable):
            await delete_function


def _delete_local(identifier, file_type, **kwargs):
    file_path = os.path.join(DATA_PATH, file_type, identifier)

    if os.path.isfile(file_path):
        os.remove(file_path)

    if file_type == 'backup':
        previousver_file_path = f'{file_path}.previousver'
        if os.path.isfile(previousver_file_path):
            os.remove(previousver_file_path)


async def load(identifier, file_type, self_hosted_config=None):
    return await router(
        identifier,
        file_type=file_type,
        self_hosted_config=self_hosted_config,
        s3_function=_load_s3,
        docker_volume_function=_load_local
    )


async def _load_s3(identifier, file_type, self_hosted_config, **kwargs):
    client = _s3_client(self_hosted_config)

    try:
        object_data = client.get_object(
            Bucket=BUCKETS.get(file_type),
            Key=f'{file_type}/{identifier}'
        )
        if isinstance(object_data, Awaitable):
            object_data = await object_data
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return b''
        else:
            raise e

    return object_data.get('Body')


def _load_local(identifier, file_type, **kwargs):
    file_path = os.path.join(DATA_PATH, file_type, identifier)

    if os.path.isfile(file_path):
        with open(file_path, 'rb') as backup_file:
            return backup_file.read()

    return b''


async def store(identifier, file_type, data, self_hosted_config=None):
    await router(
        identifier,
        file_type=file_type,
        self_hosted_config=self_hosted_config,
        s3_function=_store_s3,
        docker_volume_function=_store_local,
        data=data
    )


async def _store_s3(identifier, file_type, self_hosted_config, data, **kwargs):
    bucket = BUCKETS.get(file_type)
    key = f'{file_type}/{identifier}'

    client = _s3_client(self_hosted_config)

    if file_type == 'backup':
        try:
            copy_object = client.copy_object(Bucket=bucket, Key=f'{key}.previousver', CopySource={'Bucket': bucket, 'Key': key})
            if isinstance(copy_object, Awaitable):
                await copy_object
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                pass
            else:
                raise e

    put_object = client.put_object(
        Bucket=bucket,
        Key=key,
        Body=data
    )
    if isinstance(put_object, Awaitable):
        await put_object


def _store_local(identifier, file_type, data, **kwargs):
    directory = os.path.join(DATA_PATH, file_type)
    if not os.path.isdir(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, identifier)
    if file_type == 'backup' and os.path.isfile(file_path):
        shutil.copyfile(file_path, f'{file_path}.previousver')

    with open(file_path, 'wb') as backup_file:
        backup_file.write(data)
