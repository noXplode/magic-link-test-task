from .forms import EmailForm
from .models import EmailToken
from .views import is_added

from django.test import TestCase
from django.urls import reverse


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
        tkn = EmailToken.objects.create(email='test@test.com', active=False, entered=0)
        self.assertEqual(tkn.__str__(), f'{tkn.token}, {tkn.email}')

    def test_increase_visit(self):
        """
        increase_visit() method must increase 1
        """
        tkn = EmailToken.objects.create(email='test@test.com', active=False, entered=0)
        visits = tkn.entered
        tkn.increase_visit()
        self.assertEqual(tkn.entered - visits, 1)


class AddemailTest(TestCase):

    def test_addemail_template_status(self):
        """
        addemail() uses articles/blog.html template
        addemail() returns status_code 200
        """
        response = self.client.get(reverse('linksapp:addemail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "linksapp/email.html")

    def test_valid_form(self):
        """
        form must be valid with test email
        """
        data = {'email': 'test@email.com'}
        response = self.client.post(reverse('linksapp:addemail'), data)
        self.assertRedirects(response, reverse('linksapp:addemail'))

    def test_is_added(self):
        EmailToken.objects.create(email='test@test.com', active=True)
        self.assertEqual(is_added('test@test.com'), True)
        self.assertEqual(is_added('test1@test.com'), False)
        self.assertEqual(is_added('test@test1.com'), False)


class TokenAuthTest(TestCase):

    def test_valid_token_auth(self):
        """
        valid token must redirect to tokenlist
        session must contain valid token
        """
        tkn = EmailToken.objects.create(email='test@test.com', active=True)
        token = tkn.token
        response = self.client.get(reverse('linksapp:token_auth', args=[token]))
        session = self.client.session
        self.assertRedirects(response, reverse('linksapp:tokenslist'))
        self.assertEqual(session['emailtoken'], token.hex)

    def test_not_valid_token(self):
        """
        non valid token must redirect to 404
        """
        response = self.client.get(reverse('linksapp:token_auth', args=['de56490a-54ea-48f4-b2ba-8ac86cb8dd1b']))
        self.assertEqual(response.status_code, 404)

    def test_not_active_token(self):
        """
        valid not active token must redirect to 404
        """
        tkn = EmailToken.objects.create(email='test@test.com', active=False)
        token = tkn.token
        response = self.client.get(reverse('linksapp:token_auth', args=[token]))
        self.assertEqual(response.status_code, 404)

    def test_tokenlist_auth(self):
        """
        user with valid session emailtoken redirects to tokenslist
        """
        tkn = EmailToken.objects.create(email='test@test.com', active=True)
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
