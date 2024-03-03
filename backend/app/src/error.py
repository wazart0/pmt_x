from datetime import datetime, timezone


def error_details(code: dict, user_id, object = None) -> dict:
    return dict(**code, sub=str(user_id), obj=object, timestamp=datetime.now(timezone.utc).isoformat())


class Error:
    CREATE_TOKEN = {
        'code': 1234,
        'message': 'Incorrect credentials'
    }
    CREATE_USER = {
        'code': 1235,
        'message': 'Username is reserved'
    }
    PATCH_USER = {
        'code': 1236,
        'message': 'Username is reserved'
    }
    PATCH_OBJECT_1 = {
        'code': 1237,
        'message': 'Object not found'
    }
    PATCH_OBJECT_2 = {
        'code': 1238,
        'message': 'Object not found'
    }
    GET_OBJECT_1 = {
        'code': 1239,
        'message': 'Object not found'
    }
    GET_OBJECT_2 = {
        'code': 1240,
        'message': 'Object not found'
    }
    GET_OBJECTS = {
        'code': 1241,
        'message': 'Cannot order by provided field'
    }
    PATCH_OBJECT_3 = {
        'code': 1242,
        'message': 'Integrity error found'
    }
    CREATE_OBJECT = {
        'code': 1243,
        'message': 'Integrity error found'
    }
