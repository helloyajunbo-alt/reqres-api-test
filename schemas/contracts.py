"""响应结构契约（第四层断言的基础）。字段契约来自 ReqRes 官方文档与真实响应的交叉确认。"""

LOGIN_OK = {
    'type': 'object',
    'required': ['token'],
    'properties': {
        'token': {'type': 'string', 'minLength': 1},
    },
}

USER_ITEM = {
    'type': 'object',
    'required': ['id', 'email', 'first_name', 'last_name', 'avatar'],
    'properties': {
        'id': {'type': 'integer'},
        'email': {'type': 'string', 'pattern': r'^[^@]+@[^@]+\.[^@]+$'},
        'first_name': {'type': 'string'},
        'last_name': {'type': 'string'},
        'avatar': {'type': 'string', 'format': 'uri'},
    },
    'additionalProperties': False,
}

USER_LIST = {
    'type': 'object',
    'required': ['page', 'per_page', 'total', 'total_pages', 'data'],
    'properties': {
        'page': {'type': 'integer', 'minimum': 1},
        'per_page': {'type': 'integer', 'minimum': 1},
        'total': {'type': 'integer', 'minimum': 0},
        'total_pages': {'type': 'integer', 'minimum': 0},
        'data': {'type': 'array', 'items': USER_ITEM},
    },
}

USER_DETAIL = {
    'type': 'object',
    'required': ['data'],
    'properties': {'data': USER_ITEM},
}

USER_CREATE = {
    'type': 'object',
    'required': ['id', 'createdAt'],
    'properties': {
        'id': {'type': 'string', 'minLength': 1},
        'createdAt': {'type': 'string', 'pattern': r'\d{4}-\d{2}-\d{2}T'},
    },
}

USER_UPDATE = {
    'type': 'object',
    'required': ['name', 'job', 'updatedAt'],
    'properties': {
        'name': {'type': 'string'},
        'job': {'type': 'string'},
        'updatedAt': {'type': 'string', 'pattern': r'\d{4}-\d{2}-\d{2}T'},
    },
}
