import json

async def unauthorized_handler(session):
    if not session.get('me'):
        return json.dumps({"message": "Unauthorized", "code": 401}), 401


def check_authorization(session):
    def decorator(func):
        async def wrapper(*args, **kwargs):
                if not session.get('me'):
                     return await unauthorized_handler(session)

                return await func(*args, **kwargs)

        return wrapper

    return decorator