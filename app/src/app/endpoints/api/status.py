from app.shared.handler import lambda_handler


@lambda_handler
async def handler(**kwargs):
    return 200, {'state': 'online'}
