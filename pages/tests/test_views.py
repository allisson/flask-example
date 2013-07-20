# -*- coding: utf-8 -*-
from flask import url_for
from common.tests import BaseTestCase


class IndexViewTest(BaseTestCase):

    def test_render(self):
        resp = self.client.get(url_for('pages_app.index'))
        self.assertStatus(resp, 200)


class AboutViewTest(BaseTestCase):

    def test_render(self):
        resp = self.client.get(url_for('pages_app.about'))
        self.assertStatus(resp, 200)
