import asyncio
import functools
import json
import logging

from settings import settings


def lambda_handler(schema=None):
    def wrapper(handler):
        @functools.wraps(handler)
        def _func(event, context, coro=False):
            async def _async():
                try:
                    values = None

                    if schema and not callable(schema):
                        if event.get('httpMethod') == 'POST':
                            values = await schema.load(event.get('body'))
                        else:
                            values = await schema.load(event.get('queryStringParameters', {}))

                        if values.error:
                            return 400, {'error': values.error}

                    response = await handler(event=event, context=context, values=values)

                    if isinstance(response, dict):
                        status_code, return_value = response.get('statusCode'), response.get('body')
                    else:
                        status_code, return_value = response
                except Exception as e:
                    status_code, return_value = 500, {'message': 'Internal server error'}
                    if settings.debug:
                        logging.getLogger('exception').exception('Uncaught exception: {}'.format(str(e)))
                        return_value['error'] = str(e)

                if isinstance(return_value, dict) or isinstance(return_value, list):
                    return_value = json.dumps(return_value)

                return {
                    'statusCode': status_code,
                    'body': return_value
                }

            if coro:
                return _async()
            else:
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(_async())

        return _func

    if callable(schema):
        return wrapper(schema)

    return wrapper
