# -*- coding: utf-8 -*-
from flask import render_template, current_app
from wtforms import *
from flask.ext.wtf import Form
from flask_mail import Message

from application import mail
from common.utils import get_signer
from accounts.models import User


class LoginForm(Form):

    user = None

    username = TextField(
        label=u'Login',
        validators=[
            validators.required()
        ]
    )

    password = PasswordField(
        label=u'Password',
        validators=[
            validators.required()
        ]
    )

    next = HiddenField()

    def validate_username(form, field):
        username = field.data
        try:
            form.user = User.objects.get(username=username)
        except:
            raise ValidationError(u'Login not found.')

    def validate_password(form, field):
        password = field.data
        if form.user:
            if not form.user.check_password(password):
                raise ValidationError(u'Incorrect password.')


class SignupForm(Form):

    email = TextField(
        label=u'E-mail',
        validators=[
            validators.required(),
            validators.length(max=100),
            validators.Email()
        ]
    )

    def validate_email(form, field):
        email = field.data
        if User.objects.filter(email=email):
            raise ValidationError(u'E-mail in use.')

    def save(self):
        email = self.email.data
        site_name = current_app.config['PROJECT_SITE_NAME']
        site_url = current_app.config['PROJECT_SITE_URL']
        sender = current_app.config['MAIL_DEFAULT_SENDER']

        # create signed data
        s = get_signer()
        data = {
            'email': email,
            'signup': True
        }
        signed_data = s.dumps(data)

        # set context to template render
        context = dict(
            site_name=site_name,
            site_url=site_url,
            email=email,
            signed_data=signed_data
        )

        # load template
        html = render_template(
            'accounts/emails/signup.html', **context
        )

        # create and send message
        msg = Message(
            u'Confirm your account - {0}.'.format(site_name),
            sender=sender,
            recipients=[email]
        )
        msg.html = html
        mail.send(msg)


class SignupConfirmForm(Form):

    name = TextField(
        label=u'Name',
        validators=[
            validators.required(),
            validators.length(max=100)
        ]
    )

    username = TextField(
        label=u'Login',
        validators=[
            validators.required(),
            validators.length(min=3, max=30),
            validators.Regexp(
                regex=r'^[\w]+$',
                message=u'Just letters and numbers.'
            )
        ]
    )

    password = PasswordField(
        label=u'Password',
        validators=[
            validators.required(),
            validators.length(min=6, max=16)
        ]
    )

    password_confirm = PasswordField(
        label=u'Password Confirm',
        validators=[
            validators.required()
        ]
    )

    next = HiddenField()

    def validate_username(form, field):
        username = field.data
        if User.objects.filter(username=username):
            raise ValidationError(u'Login in use.')

    def validate_password_confirm(form, field):
        password = form.password.data
        password_confirm = field.data
        if password != password_confirm:
            raise ValidationError(u'Incorrect password.')

    def save(self, email):
        name = self.name.data
        username = self.username.data
        password = self.password.data
        email = email

        user = User(name=name, username=username, password=password, email=email)
        user.save()
        return user


class RecoverPasswordForm(Form):

    email = TextField(
        label=u'E-mail',
        validators=[
            validators.required(),
            validators.length(max=100),
            validators.Email()
        ]
    )

    def validate_email(form, field):
        email = field.data
        if not User.objects.filter(email=email):
            raise ValidationError(u'E-mail not found.')

    def save(self):
        email = self.email.data
        site_name = current_app.config['PROJECT_SITE_NAME']
        site_url = current_app.config['PROJECT_SITE_URL']
        sender = current_app.config['MAIL_DEFAULT_SENDER']

        # create signed data
        s = get_signer()
        data = {
            'email': email,
            'recover-password': True
        }
        signed_data = s.dumps(data)

        # set context to template render
        context = dict(
            site_name=site_name,
            site_url=site_url,
            email=email,
            signed_data=signed_data
        )

        # load template
        html = render_template(
            'accounts/emails/recover_password.html', **context
        )

        # create and send message
        msg = Message(
            u'Recover your password - {0}.'.format(site_name),
            sender=sender,
            recipients=[email]
        )
        msg.html = html
        mail.send(msg)


class RecoverPasswordConfirmForm(Form):

    password = PasswordField(
        label=u'Password',
        validators=[
            validators.required(),
            validators.length(min=6, max=16)
        ]
    )

    password_confirm = PasswordField(
        label=u'Password Confirm',
        validators=[
            validators.required()
        ]
    )

    def validate_password_confirm(form, field):
        password = form.password.data
        password_confirm = field.data
        if password != password_confirm:
            raise ValidationError(u'Incorrect password.')

    def save(self):
        password = self.password.data
        self.user.set_password(password)
        self.user.save()
        return self.user
