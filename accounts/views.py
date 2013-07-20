# -*- coding: utf-8 -*-
from flask import (
    Blueprint, render_template, session, g, flash, request, redirect, url_for,
    current_app
)
from accounts.models import User
from accounts.forms import (
    LoginForm, SignupForm, SignupConfirmForm, RecoverPasswordForm,
    RecoverPasswordConfirmForm
)
from common.utils import get_signer


accounts_app = Blueprint('accounts_app', __name__)


@accounts_app.before_app_request
def load_user():
    g.user = None
    if 'user_id' in session:
        try:
            g.user = User.objects.get(pk=session['user_id'])
        except:
            pass


@accounts_app.route('/login/', methods=['GET', 'POST'])
def login():
    next = request.values.get('next', '/')
    form = LoginForm()
    form.next.data = next
    if form.validate_on_submit():
        session['user_id'] = unicode(form.user.pk)
        flash(u'Login successfully', 'success')
        return redirect(next)
    return render_template('accounts/login.html', form=form)


@accounts_app.route('/logout/')
def logout():
    next = request.args.get('next', '/')
    flash(u'Logout successfully', 'success')
    session.pop('user_id', None)
    return redirect(next)


@accounts_app.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        form.save()
        flash(
            u'Check your email to confirm registration.',
            'success'
        )
        return redirect(url_for('pages_app.index'))
    return render_template('accounts/signup.html', form=form)


@accounts_app.route('/signup/<token>/', methods=['GET', 'POST'])
def signup_confirm(token):
    s = get_signer()
    try:
        signed_data = s.loads(
            token, max_age=current_app.config['PROJECT_SIGNUP_TOKEN_MAX_AGE']
        )
        email = signed_data['email']
        signup = signed_data['signup']
    except:
        flash(u'Invalid activation Link.', 'error')
        return redirect(url_for('accounts_app.signup'))

    if User.objects.filter(email=email):
        flash(u'E-mail in use.', 'error')
        return redirect(url_for('accounts_app.signup'))

    next = request.values.get('next', '/')

    form = SignupConfirmForm()
    form.next.data = next
    if form.validate_on_submit():
        user = form.save(email=email)
        session['user_id'] = unicode(user.pk)
        flash(u'Account registered successfully.', 'success')
        return redirect(next)
    return render_template('accounts/signup_confirm.html', form=form, token=token)


@accounts_app.route('/recover-password/', methods=['GET', 'POST'])
def recover_password():
    form = RecoverPasswordForm()
    if form.validate_on_submit():
        form.save()
        flash(
            u'Check it out at your email instructions for setting a new password.',
            'success'
        )
        return redirect(url_for('pages_app.index'))
    return render_template('accounts/recover_password.html', form=form)


@accounts_app.route('/recover-password/<token>/', methods=['GET', 'POST'])
def recover_password_confirm(token):
    s = get_signer()
    try:
        signed_data = s.loads(
            token, max_age=current_app.config['PROJECT_RECOVER_PASSWORD_TOKEN_MAX_AGE']
        )
        email = signed_data['email']
        recover_password = signed_data['recover-password']
    except:
        flash(u'Invalid Link.', 'error')
        return redirect(url_for('pages_app.index'))

    try:
        user = User.objects.get(email=email)
    except:
        flash(u'E-mail not found.', 'error')
        return redirect(url_for('pages_app.index'))

    form = RecoverPasswordConfirmForm()
    form.user = user
    if form.validate_on_submit():
        user = form.save()
        flash(u'Password set successfully.', 'success')
        return redirect(url_for('accounts_app.login'))
    return render_template(
        'accounts/recover_password_confirm.html',
        form=form, token=token, user=user
    )
