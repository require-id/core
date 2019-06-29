import asyncio
import json
import os
import shutil

import boto3

BUCKET = 'require-id-bucket'
LOCAL_DIRECTORY = '/backups'


def s3_backup(key, data):
    # SMELL: don't really know if this works credential wise
    client = boto3.client('s3')
    client.put_object(
        Bucket=BUCKET,
        Key=f'backups/{key}',
        Body=data
    )


def local_backup(identifier, encrypted_data_bytes):
    backup_file_path = os.path.join(LOCAL_DIRECTORY, identifier)
    if os.path.isfile(backup_file_path):
        shutil.copyfile(backup_file_path, f'{backup_file_path}.lastver')

    with open(backup_file_path) as backup_file:
        backup_file.write(encrypted_data_bytes)


async def handler(event, context):
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
        if BUCKET:
                s3_backup(key=identifier, data=encrypted_data_bytes)
        else:
            local_backup(identifier, encrypted_data_bytes)
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
