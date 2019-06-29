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
    method = event.get('httpMethod')
    body = event.get('body')

    if method not in ('POST', ):
        return {
            'statusCode': 405,
            'body': json.dumps({'message': 'Method Not Allowed'})
        }

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
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal Server Error', 'error': f'{e}'})
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Data backed up'})
    }


def run(event, context):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(handler(event, context))
