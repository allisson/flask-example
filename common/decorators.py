# -*- coding: utf-8 -*-
from functools import wraps
from flask import request


def get_page(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        page = request.args.get('page', 1)
        try:
            kwargs['page'] = int(page)
        except:
            kwargs['page'] = 1
        return f(*args, **kwargs)
    return decorated_function
