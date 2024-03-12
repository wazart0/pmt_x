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
    CREATE_BASELINE_TASK_1 = {
        'code': 1244,
        'message': 'Object not found'
    }
    CREATE_BASELINE_TASK_2 = {
        'code': 1245,
        'message': 'Object not found'
    }
    CREATE_BASELINE_TASK_3 = {
        'code': 1246,
        'message': 'Integrity error found'
    }
    PATCH_BASELINE_TASK_1 = {
        'code': 1247,
        'message': 'Object not found'
    }
    PATCH_BASELINE_TASK_2 = {
        'code': 1248,
        'message': 'Object not found'
    }
    PATCH_BASELINE_TASK_3 = {
        'code': 1249,
        'message': 'Object not found'
    }
    PATCH_BASELINE_TASK_4 = {
        'code': 1250,
        'message': 'Object not found'
    }
    GET_BASELINE_TASK_1 = {
        'code': 1251,
        'message': 'Object not found'
    }
    GET_BASELINE_TASK_2 = {
        'code': 1252,
        'message': 'Object not found'
    }
    GET_BASELINE_TASK_3 = {
        'code': 1253,
        'message': 'Object not found'
    }
    GET_BASELINE_TASKS_1 = {
        'code': 1254,
        'message': 'Object not found'
    }
    CREATE_BASELINE_TASK_PREDECESSOR_1 = {
        'code': 1255,
        'message': 'Object not found'
    }
    CREATE_BASELINE_TASK_PREDECESSOR_2 = {
        'code': 1256,
        'message': 'Object not found'
    }
    CREATE_BASELINE_TASK_PREDECESSOR_3 = {
        'code': 1257,
        'message': 'Object not found'
    }
    CREATE_BASELINE_TASK_PREDECESSOR_4 = {
        'code': 1258,
        'message': 'Integrity error found'
    }
    DELETE_BASELINE_TASK_PREDECESSOR_1 = {
        'code': 1259,
        'message': 'Object not found'
    }
    DELETE_BASELINE_TASK_PREDECESSOR_2 = {
        'code': 1260,
        'message': 'Object not found'
    }
    DELETE_BASELINE_TASK_PREDECESSOR_3 = {
        'code': 1261,
        'message': 'Object not found'
    }
    DELETE_BASELINE_TASK_PREDECESSOR_4 = {
        'code': 1262,
        'message': 'Object not found'
    }
    DELETE_BASELINE_TASK_PREDECESSOR_5 = {
        'code': 1263,
        'message': 'Integrity error found'
    }
    GET_BASELINE_PREDECESSORS_1 = {
        'code': 1264,
        'message': 'Object not found'
    }
    