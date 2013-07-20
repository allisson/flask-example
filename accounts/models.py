# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

from datetime import datetime
from application import db
from common.models import BaseDocument


class User(BaseDocument):

    username = db.StringField(
        verbose_name=u'login',
        max_length=30,
        required=True,
        unique=True
    )

    name = db.StringField(
        verbose_name=u'nome',
        max_length=100
    )

    email = db.EmailField(
        verbose_name=u'e-mail',
        max_length=100,
        required=True,
        unique=True
    )

    pw_hash = db.StringField(
        verbose_name=u'senha',
        max_length=100,
        required=True
    )

    is_active = db.BooleanField(
        verbose_name=u'ativo',
        default=True,
        required=True
    )

    is_superuser = db.BooleanField(
        verbose_name=u'super usuário',
        default=False,
        required=True
    )

    last_login = db.DateTimeField(
        verbose_name=u'último login',
        required=False
    )

    meta = {
        'indexes': ['username', 'email']
    }

    def __unicode__(self):
        return self.username

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        password = kwargs.pop('password', None)
        if password:
            self.set_password(password)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(
            password, method=current_app.config['PROJECT_PASSWORD_HASH_METHOD']
        )

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def refresh_last_login(self):
        self.last_login = datetime.now()
        self.save()
