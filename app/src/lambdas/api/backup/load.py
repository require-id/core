import asyncio
import json
import os

import boto3

BUCKET = None  # 'require-id-bucket'
LOCAL_DIRECTORY = '/app/backup'


def get_s3_backup(identifier):
    # SMELL: don't really know if this works credential wise
    client = boto3.client('s3')
    return client.get_object(
        Bucket=BUCKET,
        Key=f'backup/{identifier}'
    ).get('Body')


def get_local_backup(identifier):
    backup_file_path = os.path.join(LOCAL_DIRECTORY, identifier)
    if os.path.isfile(backup_file_path):
        with open(backup_file_path) as backup_file:
            return backup_file.read()


async def handler(event, context, self_hosted_config=None):
    aws_request_id = context.aws_request_id
    method = event.get('httpMethod')
    body = event.get('body')

    if method not in ('HEAD', 'GET'):
        return 405, json.dumps({'message': 'Method Not Allowed'})

    json_data = json.loads(body)
    identifier = json_data.get('identifier')

    if not self_hosted_config:
        backup_data = get_s3_backup(key=identifier)
    else:
        if self_hosted_config.backup_storage_method == 'local':
            backup_data = get_local_backup(identifier)
        elif self_hosted_config.backup_storage_method == 's3':
            # here you should add an async s3 method
            pass
        else:
            return 404, json.dumps({'message': 'No backup data found.'})

    if not backup_data:
        return 404, json.dumps({'message': 'No backup data found.'})

    return 200, f'{method} – backup.load: {aws_request_id}'
