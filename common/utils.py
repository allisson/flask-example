# -*- coding: utf-8 -*-
from flask import current_app
from itsdangerous import URLSafeTimedSerializer


def get_signer():
    secret = current_app.config['SECRET_KEY']
    s = URLSafeTimedSerializer(secret)
    return s
