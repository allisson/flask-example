# -*- coding: utf-8 -*-
from flask import url_for, session

from common.tests import BaseTestCase
from common.utils import get_signer
from accounts.models import User
from application import mail


class LoginViewTest(BaseTestCase):

    def setUp(self):
        self.user = User(
            username='user1',
            email='user1@email.com',
            password='123456'
        ).save()
        self.url = url_for('accounts_app.login')
        self.redirect_to = url_for('pages_app.index')
        self.redirect_to_about = url_for('pages_app.about')

    def tearDown(self):
        User.drop_collection()

    def test_render(self):
        resp = self.client.get(self.url)
        self.assertStatus(resp, 200)

    def test_form(self):
        # test empty form
        with self.captured_templates(self.app) as templates:
            resp = self.client.post(self.url)
            self.assertStatus(resp, 200)
            template, context = templates[0]
            form = context['form']
            self.assertTrue(
                u'This field is required.' in form.errors['username']
            )
            self.assertTrue(
                u'This field is required.' in form.errors['password']
            )

        # test validate username
        with self.captured_templates(self.app) as templates:
            resp = self.client.post(
                self.url,
                data=dict(username='user2')
            )
            self.assertStatus(resp, 200)
            template, context = templates[0]
            form = context['form']
            self.assertTrue(
                u'Login not found.' in form.errors['username']
            )

        # test validate password
        with self.captured_templates(self.app) as templates:
            resp = self.client.post(
                self.url,
                data=dict(username='user1', password='1234567')
            )
            self.assertStatus(resp, 200)
            template, context = templates[0]
            form = context['form']
            self.assertTrue(
                u'Incorrect password.' in form.errors['password']
            )

        # test valid form
        with self.app.test_client() as c:
            self.assertFalse('user_id' in session)
            resp = c.post(
                self.url,
                data=dict(username='user1', password='123456')
            )
            self.assertRedirects(resp, self.redirect_to)
            self.assertTrue('user_id' in session)

        # test valid form redirect
        with self.captured_templates(self.app) as templates:
            resp = self.client.post(
                self.url,
                data=dict(username='user1', password='123456'),
                follow_redirects=True
            )
            self.assertStatus(resp, 200)
            template, context = templates[0]
            self.assertTrue(context['g'].user)
            self.assertTrue(
                'Login successfully' in resp.data
            )

        # test valid form redirect with next parameter
        resp = self.client.post(
            self.url,
            data=dict(
                username='user1',
                password='123456',
                next=self.redirect_to_about
            )
        )
        self.assertRedirects(resp, self.redirect_to_about)


class LogoutViewTest(BaseTestCase):

    def setUp(self):
        self.user = User(
            username='user1',
            email='user1@email.com',
            password='123456'
        ).save()
        self.url = url_for('accounts_app.logout')
        self.redirect_to = url_for('pages_app.index')
        self.redirect_to_about = url_for('pages_app.about')

    def tearDown(self):
        User.drop_collection()

    def test_render(self):
        # test logout
        with self.app.test_client() as c:
            self.login(username='user1', password='123456', client=c)
            self.assertTrue('user_id' in session)
            resp = c.get(self.url)
            self.assertRedirects(resp, self.redirect_to)
            self.assertFalse('user_id' in session)

        # test logout with next parameter
        with self.app.test_client() as c:
            self.login(username='user1', password='123456', client=c)
            self.assertTrue('user_id' in session)
            resp = c.get(self.url + '?next=' + self.redirect_to_about)
            self.assertRedirects(resp, self.redirect_to_about)
            self.assertFalse('user_id' in session)


class SignupViewTest(BaseTestCase):

    def setUp(self):
        self.user = User(
            username='user1',
            email='user1@email.com',
            password='123456'
        ).save()
        self.url = url_for('accounts_app.signup')
        self.redirect_to = url_for('pages_app.index')

    def tearDown(self):
        User.drop_collection()

    def test_render(self):
        resp = self.client.get(self.url)
        self.assertStatus(resp, 200)

    def test_form(self):
        # test empty form
        with self.captured_templates(self.app) as templates:
            resp = self.client.post(self.url)
            self.assertStatus(resp, 200)
            template, context = templates[0]
            form = context['form']
            self.assertTrue(
                u'This field is required.' in form.errors['email']
            )

        # test validate email
        with self.captured_templates(self.app) as templates:
            resp = self.client.post(
                self.url,
                data=dict(email='user1@email.com')
            )
            self.assertStatus(resp, 200)
            template, context = templates[0]
            form = context['form']
            self.assertTrue(
                u'E-mail in use.' in form.errors['email']
            )

        # test valid form
        with mail.record_messages() as outbox:
            self.assertEquals(len(outbox), 0)
            resp = self.client.post(
                self.url,
                data=dict(email='user2@email.com')
            )
            self.assertRedirects(resp, self.redirect_to)
            self.assertEquals(len(outbox), 1)
            self.assertEquals(
                outbox[0].subject,
                u'Confirm your account - Flask Example.'
            )

        # test valid form after redirect
        resp = self.client.post(
            self.url,
            data=dict(email='user1@email.com'),
            follow_redirects=True
        )
        self.assertStatus(resp, 200)
        self.assertTrue(
            'Check your email to confirm registration.' in resp.data
        )


class SignupConfirmViewTest(BaseTestCase):

    def setUp(self):
        self.s = get_signer()
        self.data = {
            'email': u'user2@email.com',
            'signup': True
        }
        self.token = self.s.dumps(self.data)
        self.data['email'] = u'user1@email.com'
        self.token2 = self.s.dumps(self.data)
        self.token3 = self.token + 'a'
        self.user = User(
            username='user1',
            email='user1@email.com',
            password='123456'
        ).save()
        self.url = url_for('accounts_app.signup_confirm', token=self.token)
        self.url2 = url_for('accounts_app.signup_confirm', token=self.token2)
        self.url3 = url_for('accounts_app.signup_confirm', token=self.token3)
        self.redirect_invalid = url_for('accounts_app.signup')
        self.redirect_to = url_for('pages_app.index')
        self.redirect_to_about = url_for('pages_app.about')

    def tearDown(self):
        User.drop_collection()

    def test_render(self):
        # test render with invalid token
        resp = self.client.get(self.url3)
        self.assertRedirects(resp, self.redirect_invalid)
        resp = self.client.get(self.url3, follow_redirects=True)
        self.assertTrue('Invalid activation Link.' in resp.data)

        # test render with registered email
        resp = self.client.get(self.url2)
        self.assertRedirects(resp, self.redirect_invalid)
        resp = self.client.get(self.url2, follow_redirects=True)
        self.assertTrue('E-mail in use.' in resp.data)

        # test render with valid token
        resp = self.client.get(self.url)
        self.assertStatus(resp, 200)

    def test_form(self):
        # test empty form
        with self.captured_templates(self.app) as templates:
            resp = self.client.post(self.url)
            self.assertStatus(resp, 200)
            template, context = templates[0]
            form = context['form']
            self.assertTrue(
                u'This field is required.' in form.errors['name']
            )
            self.assertTrue(
                u'This field is required.' in form.errors['username']
            )
            self.assertTrue(
                u'This field is required.' in form.errors['password']
            )
            self.assertTrue(
                u'This field is required.' in form.errors['password_confirm']
            )

        # test validate username
        with self.captured_templates(self.app) as templates:
            resp = self.client.post(
                self.url,
                data=dict(username='user1')
            )
            self.assertStatus(resp, 200)
            template, context = templates[0]
            form = context['form']
            self.assertTrue(
                u'Login in use.' in form.errors['username']
            )

        # test validate password_confirm
        with self.captured_templates(self.app) as templates:
            resp = self.client.post(
                self.url,
                data=dict(password='123456', password_confirm='1234567')
            )
            self.assertStatus(resp, 200)
            template, context = templates[0]
            form = context['form']
            self.assertTrue(
                u'Incorrect password.' in form.errors['password_confirm']
            )

        # test valid form
        resp = self.client.post(
            self.url,
            data=dict(
                name='Allisson Azevedo',
                username='allisson',
                password='123456',
                password_confirm='123456'
            )
        )
        self.assertRedirects(resp, self.redirect_to)
        user = User.objects.get(username='allisson')
        user.delete()

        # test valid form with next
        resp = self.client.post(
            self.url,
            data=dict(
                name='Allisson Azevedo',
                username='allisson',
                password='123456',
                password_confirm='123456',
                next=self.redirect_to_about
            )
        )
        self.assertRedirects(resp, self.redirect_to_about)
        user = User.objects.get(username='allisson')
        user.delete()

        # test valid form after redirect
        resp = self.client.post(
            self.url,
            data=dict(
                name='Allisson Azevedo',
                username='allisson',
                password='123456',
                password_confirm='123456'
            ),
            follow_redirects=True
        )
        self.assertStatus(resp, 200)
        self.assertTrue(
            'Account registered successfully.' in resp.data
        )
        user = User.objects.get(username='allisson')


class RecoverPasswordViewTest(BaseTestCase):

    def setUp(self):
        self.user = User(
            username='user1',
            email='user1@email.com',
            password='123456'
        ).save()
        self.url = url_for('accounts_app.recover_password')
        self.redirect_to = url_for('pages_app.index')

    def tearDown(self):
        User.drop_collection()

    def test_render(self):
        resp = self.client.get(self.url)
        self.assertStatus(resp, 200)

    def test_form(self):
        # test empty form
        with self.captured_templates(self.app) as templates:
            resp = self.client.post(self.url)
            self.assertStatus(resp, 200)
            template, context = templates[0]
            form = context['form']
            self.assertTrue(
                u'This field is required.' in form.errors['email']
            )

        # test validate email
        with self.captured_templates(self.app) as templates:
            resp = self.client.post(
                self.url,
                data=dict(email='user2@email.com')
            )
            self.assertStatus(resp, 200)
            template, context = templates[0]
            form = context['form']
            self.assertTrue(
                u'E-mail not found.' in form.errors['email']
            )

        # test valid form
        with mail.record_messages() as outbox:
            self.assertEquals(len(outbox), 0)
            resp = self.client.post(
                self.url,
                data=dict(email='user1@email.com')
            )
            self.assertRedirects(resp, self.redirect_to)
            self.assertEquals(len(outbox), 1)
            self.assertEquals(
                outbox[0].subject,
                u'Recover your password - Flask Example.'
            )

        # test valid form after redirect
        resp = self.client.post(
            self.url,
            data=dict(email='user1@email.com'),
            follow_redirects=True
        )
        self.assertStatus(resp, 200)
        self.assertTrue(
            'Check it out at your email instructions for setting a new password.' in resp.data
        )


class RecoverPasswordConfirmViewTest(BaseTestCase):

    def setUp(self):
        self.s = get_signer()
        self.data = {
            'email': u'user1@email.com',
            'recover-password': True
        }
        self.token = self.s.dumps(self.data)
        self.data['email'] = u'user2@email.com'
        self.token2 = self.s.dumps(self.data)
        self.token3 = self.token + 'a'
        self.user = User(
            username='user1',
            email='user1@email.com',
            password='123456'
        ).save()
        self.url = url_for('accounts_app.recover_password_confirm', token=self.token)
        self.url2 = url_for('accounts_app.recover_password_confirm', token=self.token2)
        self.url3 = url_for('accounts_app.recover_password_confirm', token=self.token3)
        self.redirect_invalid = url_for('pages_app.index')
        self.redirect_to = url_for('accounts_app.login')

    def tearDown(self):
        User.drop_collection()

    def test_render(self):
        # test render with invalid token
        resp = self.client.get(self.url3)
        self.assertRedirects(resp, self.redirect_invalid)
        resp = self.client.get(self.url3, follow_redirects=True)
        self.assertTrue('Invalid Link.' in resp.data)

        # test render with registered email
        resp = self.client.get(self.url2)
        self.assertRedirects(resp, self.redirect_invalid)
        resp = self.client.get(self.url2, follow_redirects=True)
        self.assertTrue('E-mail not found.' in resp.data)

        # test render with valid token
        resp = self.client.get(self.url)
        self.assertStatus(resp, 200)

    def test_form(self):
        # test empty form
        with self.captured_templates(self.app) as templates:
            resp = self.client.post(self.url)
            self.assertStatus(resp, 200)
            template, context = templates[0]
            form = context['form']
            self.assertTrue(
                u'This field is required.' in form.errors['password']
            )
            self.assertTrue(
                u'This field is required.' in form.errors['password_confirm']
            )

        # test validate password_confirm
        with self.captured_templates(self.app) as templates:
            resp = self.client.post(
                self.url,
                data=dict(password='123456', password_confirm='1234567')
            )
            self.assertStatus(resp, 200)
            template, context = templates[0]
            form = context['form']
            self.assertTrue(
                u'Incorrect password.' in form.errors['password_confirm']
            )

        # test valid form
        resp = self.client.post(
            self.url,
            data=dict(
                password='1234567',
                password_confirm='1234567'
            )
        )
        self.assertRedirects(resp, self.redirect_to)
        self.user = User.objects.get(pk=self.user.pk)
        self.assertTrue(self.user.check_password('1234567'))

        # test valid form after redirect
        resp = self.client.post(
            self.url,
            data=dict(
                password='12345678',
                password_confirm='12345678'
            ),
            follow_redirects=True
        )
        self.assertStatus(resp, 200)
        self.assertTrue(
            'Password set successfully.' in resp.data
        )
        self.user = User.objects.get(pk=self.user.pk)
        self.assertTrue(self.user.check_password('12345678'))
