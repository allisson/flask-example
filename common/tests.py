# -*- coding: utf-8 -*-
from flask import template_rendered, url_for

from contextlib import contextmanager
import unittest

from application import create_app


class BaseTestCase(unittest.TestCase):

    def __call__(self, result=None):
        self._pre_setup()
        super(BaseTestCase, self).__call__(result)
        self._post_teardown()

    def _pre_setup(self):
        self.app = create_app('settings_test')
        self.client = self.app.test_client()
        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def _post_teardown(self):
        self.ctx.pop()

    def assertRedirects(self, resp, location):
        self.assertTrue(resp.status_code in (301, 302))
        self.assertEqual(resp.location, 'http://localhost' + location)

    def assertStatus(self, resp, status_code):
        self.assertEqual(resp.status_code, status_code)

    def login(self, username, password, client=None):
        if client:
            client = client
        else:
            client = self.client
        resp = client.post(
            url_for('accounts_app.login'),
            data=dict(username='user1', password='123456'),
            follow_redirects=True
        )
        return resp

    def logout(self, client=None):
        if client:
            client = client
        else:
            client = self.client
        resp = client.get(
            url_for('accounts_app.logout'),
            follow_redirects=True
        )
        return resp

    @contextmanager
    def captured_templates(self, app):
        recorded = []

        def record(sender, template, context, **extra):
            recorded.append((template, context))

        template_rendered.connect(record, app)

        try:
            yield recorded
        finally:
            template_rendered.disconnect(record, app)
