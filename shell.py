#!/usr/bin/env python
import os
import readline
from pprint import pprint
from application import create_app


app = create_app('settings')


os.environ['PYTHONINSPECT'] = 'True'
