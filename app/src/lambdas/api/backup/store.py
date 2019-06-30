import asyncio
import json
import os
import shutil

import boto3

BUCKET = None  # 'require-id-bucket'
LOCAL_DIRECTORY = '/app/backup'


def s3_backup(identifier, data):
    # SMELL: don't really know if this works credential wise
    client = boto3.client('s3')
    client.put_object(
        Bucket=BUCKET,
        Key=f'backup/{identifier}',
        Body=data
    )


def local_backup(identifier, encrypted_data_bytes):
    backup_file_path = os.path.join(LOCAL_DIRECTORY, identifier)
    if os.path.isfile(backup_file_path):
        shutil.copyfile(backup_file_path, f'{backup_file_path}.lastver')

    with open(backup_file_path, 'wb') as backup_file:
        backup_file.write(encrypted_data_bytes)


async def handler(event, context, self_hosted_config=None):
    # aws_request_id = context.aws_request_id
    body = event.get('body')

    json_data = json.loads(body)
    identifier = json_data.get('identifier')
    encrypted_data = json_data.get('data')
    if isinstance(encrypted_data, str):
        encrypted_data_bytes = encrypted_data.encode('utf-8')
    try:
        if not self_hosted_config:
            s3_backup(key=identifier, data=encrypted_data_bytes)
        else:
            if self_hosted_config.backup_storage_method == 'local':
                local_backup(identifier, encrypted_data_bytes)
            elif self_hosted_config.backup_storage_method == 's3':
                # here you should add an async s3 method
                pass
    except Exception as e:
        return 500, json.dumps({'message': 'Internal Server Error', 'error': f'{e}'})

    return 200, json.dumps({'message': 'Data backed up'})
