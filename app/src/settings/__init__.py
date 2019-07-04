import app
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


def is_truthy(value):
    return True if str(value or '').lower() in ('true', '1', 'yes') else False


_config_data = json.loads(os.getenv('CONFIG_DATA') or '{}')
_aws_config_data = _config_data.get('aws', {})
_storage_method = _config_data.get('storage_method') or os.getenv('STORAGE_METHOD')

if _storage_method not in ('s3', 'docker_volume'):
    _storage_method = None

settings = Settings({
    'app_api_key': _config_data.get('app_api_key') or None,
    'data_path': _config_data.get('data_path') or os.path.abspath(os.path.join(os.path.dirname(app.__file__), '..', '..', 'data')),
    'prompt_api_key': _config_data.get('prompt_api_key') or None,
    'aws_access_key_id': None if is_truthy(os.getenv('USE_LAMBDA_ROLE')) else (_aws_config_data.get('aws_access_key_id') or os.getenv('AWS_ACCESS_KEY_ID') or None),
    'aws_secret_access_key': None if is_truthy(os.getenv('USE_LAMBDA_ROLE')) else (_aws_config_data.get('aws_secret_access_key') or os.getenv('AWS_SECRET_ACCESS_KEY') or None),
    'aws_region': _aws_config_data.get('region_name') or os.getenv('AWS_DEFAULT_REGION') or 'eu-west-1',
    'aws_s3_bucket': _aws_config_data.get('aws_s3_bucket') or os.getenv('AWS_S3_BUCKET'),
    'aws_s3_endpoint': _aws_config_data.get('aws_s3_endpoint'),
    'debug': is_truthy(_config_data.get('debug') or os.getenv('DEBUG')),
    'storage_method': _storage_method
})
