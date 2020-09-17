from .forms import EmailForm
from .models import EmailToken
from .views import is_added, mail_sender

from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages

from factory.django import DjangoModelFactory
from unittest.mock import patch


class EmailTokenFactory(DjangoModelFactory):
    class Meta:
        model = EmailToken

    email = 'test@test.com'
    active = True
    entered = 0


class EmailFormTest(TestCase):

    def test_email_form(self):
        """
        EmailForm with simple test email must be valid
        """
        form = EmailForm(data={'email': 'test@email.com'})
        self.assertTrue(form.is_valid())

    def test_email_form_not_valid(self):
        """
        EmailForm with simple test email must be valid
        """
        form = EmailForm(data={'email': 'test@email'})
        self.assertFalse(form.is_valid())


class EmailTokenModelTest(TestCase):

    def test_str_method(self):
        """
        __str__() must return f'{self.token}, {self.email}'
        """
        tkn = EmailTokenFactory()
        self.assertEqual(tkn.__str__(), f'{tkn.token}, {tkn.email}')

    def test_increase_visit(self):
        """
        increase_visit() method must increase 1
        """
        tkn = EmailTokenFactory()
        visits = tkn.entered
        tkn.increase_visit()
        self.assertEqual(tkn.entered - visits, 1)


class AddemailTest(TestCase):

    @patch('linksapp.views.mail.send_mail', return_value=1)
    @patch('linksapp.views.mail.outbox', return_value=[{'body': 'Test email message'}])
    def test_mail_sender(self, mock_outbox, mock_send_mail):
        """
        testing method with successful sending
        """
        token = EmailTokenFactory()
        url = reverse('linksapp:token_auth', args=(str(token.token),))
        result, messagetext = mail_sender(token, url)
        self.assertTrue(mock_send_mail.called)
        self.assertTrue(result)

    @patch('linksapp.views.mail.send_mail', return_value=0)
    def test_mail_sender_fail(self, mock_send_mail):
        """
        testing method with failed sending
        """
        token = EmailTokenFactory()
        url = reverse('linksapp:token_auth', args=(str(token.token),))
        result, messagetext = mail_sender(token, url)
        self.assertTrue(mock_send_mail.called)
        self.assertFalse(result)

    def test_is_added(self):
        """
        testing is_added method
        """
        EmailTokenFactory()
        self.assertEqual(is_added('test@test.com'), True)
        self.assertEqual(is_added('test1@test.com'), False)
        self.assertEqual(is_added('test@test1.com'), False)

    def test_addemail_template_status(self):
        """
        addemail() uses articles/blog.html template
        addemail() returns status_code 200
        """
        response = self.client.get(reverse('linksapp:addemail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "linksapp/email.html")

    @patch('linksapp.views.mail_sender', return_value=(True, 'Test email message'))
    def test_valid_form_with_new_email(self, mock_mail_sender):
        """
        testing new email address, email must be sent
        """
        data = {'email': 'test@email.com'}
        response = self.client.post(reverse('linksapp:addemail'), data)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(mock_mail_sender.called)
        self.assertEqual(messages[0].message, 'На email test@email.com была отправлена ссылка.')
        self.assertEqual(messages[1].message, 'Текст письма Test email message')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('linksapp:addemail'))

    @patch('linksapp.views.mail_sender', return_value=(False, ''))
    def test_valid_form_with_used_email(self, mock_mail_sender):
        """
        testing used email address, email must not be sent
        """
        EmailTokenFactory(email='test@email.com')
        data = {'email': 'test@email.com'}
        response = self.client.post(reverse('linksapp:addemail'), data)
        messages = list(get_messages(response.wsgi_request))
        self.assertFalse(mock_mail_sender.called)
        self.assertEqual(messages[0].message, 'Email test@email.com уже был добавлен. Ссылка уже была отправлена ранее.')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('linksapp:addemail'))

    @patch('linksapp.views.mail_sender', return_value=(False, ''))
    def test_valid_form_email_send_error(self, mock_mail_sender):
        """
        testing new email address with sending email error
        """
        data = {'email': 'test@email.com'}
        response = self.client.post(reverse('linksapp:addemail'), data)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(mock_mail_sender.called)
        self.assertEqual(messages[0].message, 'Ошибка отправки')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('linksapp:addemail'))


class TokenAuthTest(TestCase):

    def test_valid_token_auth(self):
        """
        valid token must redirect to tokenlist
        session must contain valid token
        """
        tkn = EmailTokenFactory()
        token = tkn.token
        response = self.client.get(reverse('linksapp:token_auth', args=[token]))
        session = self.client.session
        self.assertRedirects(response, reverse('linksapp:tokenslist'))
        self.assertEqual(session['emailtoken'], token.hex)

    @patch('linksapp.views.is_valid', return_value=False)
    def test_not_valid_token(self, mock_is_valid):
        """
        non valid token must redirect to 404
        """
        response = self.client.get(reverse('linksapp:token_auth', args=['de56490a-54ea-48f4-b2ba-8ac86cb8dd1b']))
        self.assertTrue(mock_is_valid.called)
        self.assertEqual(response.status_code, 404)

    @patch('linksapp.views.is_valid', return_value=False)
    def test_not_active_token(self, mock_is_valid):
        """
        valid not active token must redirect to 404
        """
        tkn = EmailTokenFactory()
        response = self.client.get(reverse('linksapp:token_auth', args=[tkn.token]))
        self.assertTrue(mock_is_valid.called)
        self.assertEqual(response.status_code, 404)


class TokenslistTest(TestCase):

    def test_tokenlist_auth(self):
        """
        user with valid session emailtoken redirects to tokenslist
        """
        tkn = EmailTokenFactory()
        session = self.client.session
        session['emailtoken'] = tkn.token.hex
        session.save()
        response = self.client.get(reverse('linksapp:tokenslist'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "linksapp/tokens.html")

    def test_tokenlist_auth_decline_not_valid(self):
        """
        user without valid session emailtoken redirects 404
        """
        self.client.session['emailtoken'] = 'de56490a-54ea-48f4-b2ba-8ac86cb8dd1u'
        response = self.client.get(reverse('linksapp:tokenslist'))
        self.assertEqual(response.status_code, 404)

    def test_tokenlist_auth_decline(self):
        """
        user without session emailtoken redirects 404
        """
        response = self.client.get(reverse('linksapp:tokenslist'))
        self.assertEqual(response.status_code, 404)
