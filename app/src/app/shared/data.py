import asyncio
import json
import os
from typing import Awaitable

import aiobotocore
import botocore

from app.shared.exceptions import InvalidConfigError


BUCKETS = json.loads(os.environ['BUCKETS'])


async def router(event, context, self_hosted_config, file_type, s3_function, docker_volume_function):
    body = event.get('body')

    json_data = json.loads(body)
    identifier = json_data.get('identifier')
    if not self_hosted_config or self_hosted_config.storage_method == 's3':
        return await s3_function(identifier, file_type, self_hosted_config=self_hosted_config)
    elif self_hosted_config.storage_method == 'docker_volume':
        return docker_volume_function(identifier, file_type)
    else:
        raise InvalidConfigError


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


async def _delete_s3(identifier, file_type, self_hosted_config=None):
    bucket = BUCKETS.get(file_type)
    key = f'{file_type}/{identifier}'

    list_object_versions_data = {
        'Bucket': bucket,
        'Prefix': key
    }
    client = _s3_client(self_hosted_config)
    versions = client.list_object_versions(**list_object_versions_data)
    if isinstance(versions, Awaitable):
        versions = await versions

    for object_version in versions.get('Versions'):
        delete_object_data = {
            'Bucket': bucket,
            'Key': key,
            'VersionId': object_version.get('VersionId'),
        }
        delete_function = client.delete_object(**delete_object_data)
        if isinstance(delete_function, Awaitable):
            await delete_function


def _delete_local(identifier, file_type):
    file_path = os.path.join(f'/app/{file_type}', identifier)
    if os.path.isfile(file_path):
        os.remove(file_path)

    if not file_type == 'backup':
        return
    previousver_file_path = f'{file_path}.previousver'
    if os.path.isfile(previousver_file_path):
        os.remove(previousver_file_path)


async def delete(event, context, self_hosted_config, file_type):
    await router(
        event,
        context,
        self_hosted_config,
        file_type=file_type,
        s3_function=_delete_s3,
        docker_volume_function=_delete_local
    )
