import json
import os

import boto3

from lambdas.exceptions import InvalidConfigError

BUCKET = None  # 'require-id-bucket'
LOCAL_DIRECTORY = '/app/backup'


def delete_s3_backups(identifier):
    # SMELL: don't really know if this works credential wise
    s3 = boto3.resource('s3')
    versions = s3.Bucket(BUCKET).object_versions.filter(
        Prefix=f'backup/{identifier}'
    )
    for version in versions:
        s3_object = version.get()
        s3_object.delete()

        # not sure if anything else is needed
        # #but otherwise you get the version like this
        # version_id = s3_object.get('VersionId')


def delete_local_backups(identifier):
    backup_file_path = os.path.join(LOCAL_DIRECTORY, identifier)
    if os.path.isfile(backup_file_path):
        os.remove(backup_file_path)

    lastver_backup_file_path = f'{backup_file_path}.lastver'
    if os.path.isfile(lastver_backup_file_path):
        os.remove(lastver_backup_file_path)


async def handler(event, context, self_hosted_config=None):
    aws_request_id = context.aws_request_id

    await runner(
        event,
        context,
        self_hosted_config,
        delete_s3_backups,
        delete_local_backups,
        delete_s3_backups_async
    )

    return 200, f'backup.delete: {aws_request_id}'


async def runner(event, context, self_hosted_config, lambda_function, docker_volume_function, async_function):
    body = event.get('body')

    json_data = json.loads(body)
    identifier = json_data.get('identifier')
    if not self_hosted_config:
            lambda_function(identifier)
    else:
        if self_hosted_config.backup_storage_method == 'docker_volume':
            docker_volume_function(identifier)
        elif self_hosted_config.backup_storage_method == 's3':
            await async_function(identifier)
            pass
        else:
            raise InvalidConfigError
