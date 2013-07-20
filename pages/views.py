# -*- coding: utf-8 -*-
from flask import Blueprint, render_template


pages_app = Blueprint('pages_app', __name__)


@pages_app.route('/')
def index():
    return render_template('pages/index.html')


@pages_app.route('/about/')
def about():
    return render_template('pages/about.html')
