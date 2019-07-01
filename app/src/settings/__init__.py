import json
import os


class Settings:
    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return self._data.get(key)

    def __getattr__(self, key):
        return self._data.get(key)

    def __contains__(self, item):
        return self._data.__contains__(item)

    def __eq__(self, other):
        if isinstance(other, Settings):
            return self._data == other._data
        elif isinstance(other, dict):
            return self._data == other
        else:
            return False

    def keys(self):
        return self._data.keys()

    def get(self, key, default=None):
        return self._data.get(key, default)


_config_data = json.loads(os.getenv('CONFIG_DATA') or '{}')
_storage_method = _config_data.get('storage_method') or os.getenv('STORAGE_METHOD')

if _storage_method not in ('s3', 'docker_volume'):
    _storage_method = None

settings = Settings({
    'api_key': _config_data.get('api_key'),
    'aws_access_key_id': _config_data.get('aws', {}).get('aws_access_key_id') or os.getenv('AWS_ACCESS_KEY_ID'),
    'aws_secret_access_key': _config_data.get('aws', {}).get('aws_secret_access_key') or os.getenv('AWS_SECRET_ACCESS_KEY'),
    'aws_region': _config_data.get('aws', {}).get('aws_region') or os.getenv('AWS_DEFAULT_REGION') or 'eu-west-1',
    'aws_s3_bucket':  _config_data.get('aws', {}).get('aws_s3_bucket') or os.getenv('AWS_S3_BUCKET'),
    'aws_s3_endpoint': _config_data.get('endpoints', {}).get('aws_s3'),
    'storage_method': _storage_method
})
