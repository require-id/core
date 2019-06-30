import asyncio
import json
import os

import aiobotocore
import boto3

from shared.exceptions import InvalidConfigError


BUCKETS = json.loads(os.environ['BUCKETS'])


async def router(event, context, self_hosted_config, file_type, s3_function, docker_volume_function):
    body = event.get('body')

    json_data = json.loads(body)
    identifier = json_data.get('identifier')
    if not self_hosted_config:
        return s3_function(identifier, file_type)
    else:
        if self_hosted_config.backup_storage_method == 'docker_volume':
            return docker_volume_function(identifier, file_type)
        elif self_hosted_config.backup_storage_method == 's3':
            return await delete_s3(identifier, file_type=file_type, self_hosted_config=self_hosted_config)
        else:
            raise InvalidConfigError


async def s3_client(self_hosted_config):
    session = aiobotocore.get_session(loop=asyncio.get_event_loop())
    client = session.create_client(
        's3',
        region_name='us-west-1',
        aws_secret_access_key=self_hosted_config.aws_secret_access_key,
        aws_access_key_id=self_hosted_config.aws_access_key_id,
        endpoint=self_hosted_config.aws_s3_endpoint
    )
    return client


async def delete_s3(identifier, file_type, self_hosted_config=None, asynchronous=False):
    # SMELL: don't really know if this works credential wise
    if not asynchronous:
        s3 = boto3.resource('s3')
        versions = s3.Bucket(BUCKETS.get(file_type)).object_versions.filter(
            Prefix=f'{file_type}/{identifier}'
        )
        for version in versions:
            s3_object = version.get()
            s3_object.delete()

            # not sure if anything else is needed
            # #but otherwise you get the version like this
            # version_id = s3_object.get('VersionId')
    else:
        client = await s3_client(self_hosted_config)
        await client.delete_object(
            Bucket=self_hosted_config.get(file_type).get('s3_bucket'),
            Key=f'{file_type}/{identifier}'
        )


def delete_local(identifier, file_type):
    backup_file_path = os.path.join(f'/app/{file_type}', identifier)
    if os.path.isfile(backup_file_path):
        os.remove(backup_file_path)

    lastver_backup_file_path = f'{backup_file_path}.lastver'
    if os.path.isfile(lastver_backup_file_path):
        os.remove(lastver_backup_file_path)


async def delete(event, context, self_hosted_config, file_type):
    await router(
        event,
        context,
        self_hosted_config,
        file_type=file_type,
        s3_function=delete_s3,
        docker_volume_function=delete_local
    )
