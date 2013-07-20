#!/usr/bin/env python
# -*- coding: utf-8 -*-
from application import create_app
app = create_app('settings')
app.run()
