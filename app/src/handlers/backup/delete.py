import asyncio
import json
import os

import boto3

BUCKET = None  # 'require-id-bucket'
LOCAL_DIRECTORY = '/backups'


def delete_s3_backups(identifier):
    s3 = boto3.resource('s3')
    versions = s3.Bucket(BUCKET).object_versions.filter(
        Prefix=f'backups/{identifier}'
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


async def handler(event, context):
    aws_request_id = context.aws_request_id
    method = event.get('httpMethod')
    body = event.get('body')

    if method not in ('POST', ):
        return {
            'statusCode': 405,
            'body': json.dumps({'message': 'Method Not Allowed'})
        }

    json_data = json.loads(body)
    identifier = json_data.get('identifier')

    if BUCKET:
        delete_s3_backups(identifier)
    else:
        delete_local_backups(identifier)

    return {
        'statusCode': 200,
        'body': f'{method} – backup.delete: {aws_request_id}'
    }


def run(event, context):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(handler(event, context))
