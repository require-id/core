import asyncio
import json
import os

import boto3

BUCKET = None  # 'require-id-bucket'
LOCAL_DIRECTORY = '/backups'


def get_s3_backup(identifier):
    # SMELL: don't really know if this works credential wise
    client = boto3.client('s3')
    return client.get_object(
        Bucket=BUCKET,
        Key=f'backups/{identifier}'
    ).get('Body')


def get_local_backup(identifier):
    backup_file_path = os.path.join(LOCAL_DIRECTORY, identifier)
    if os.path.isfile(backup_file_path):
        with open(backup_file_path) as backup_file:
            return backup_file.read()


async def handler(event, context):
    aws_request_id = context.aws_request_id
    method = event.get('httpMethod')
    body = event.get('body')

    if method not in ('HEAD', 'GET'):
        return {
            'statusCode': 405,
            'body': json.dumps({'message': 'Method Not Allowed'})
        }

    json_data = json.loads(body)
    identifier = json_data.get('identifier')

    if BUCKET:  # SMELL: maybe change this to some sort of setting from tomodachi
        backup_data = get_s3_backup(key=identifier)
    else:
        backup_data = get_local_backup(identifier)

    if not backup_data:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'No backup data found.'})
        }

    return {
        'statusCode': 200,
        'body': f'{method} – backup.load: {aws_request_id}'
    }


def run(event, context):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(handler(event, context))
