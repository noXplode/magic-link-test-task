from .forms import EmailForm
from .models import EmailToken
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.urls import reverse
from django.core import mail

import uuid


def is_added(email):
    try:
        EmailToken.objects.filter(email=email)[0]
    except IndexError:
        return False
    else:
        return True


def is_valid(token):
    try:
        token = EmailToken.objects.filter(active=True).filter(token=token)[0]
    except IndexError:
        return False
    else:
        return True


def mail_sender(tokenobj: EmailToken, url):
    result = mail.send_mail('URL access link', f'Here is your URL access link: {url}', 'from@example.com', [tokenobj.email], fail_silently=False, )
    if result == 1:
        message = mail.outbox[0].body
        return True, message
    else:
        return False, ''


def addemail(request):

    if request.method == 'POST':
        # if POST request
        form = EmailForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            if is_added(email) is True:
                # email was already added
                messages.add_message(request, messages.SUCCESS, f'Email {email} уже был добавлен. Ссылка уже была отправлена ранее.')
            else:
                # new email, creating new EmailToken
                new_token = EmailToken(email=email)
                new_token.save()

                # creating url for user
                url = request.build_absolute_uri(reverse('linksapp:token_auth', args=(str(new_token.token),)))

                # sending email
                result, messagetext = mail_sender(new_token, url)
                if result is True:
                    # using Django In-memory backend for testing purposes
                    messages.add_message(request, messages.SUCCESS, f'На email {new_token.email} была отправлена ссылка.')
                    messages.add_message(request, messages.SUCCESS, f'Текст письма {messagetext}')
                else:
                    messages.add_message(request, messages.ERROR, 'Ошибка отправки')

        return HttpResponseRedirect(reverse('linksapp:addemail'))
    else:
        # if GET request creating empty form
        form = EmailForm()
        return render(request, 'linksapp/email.html', {'form': form})


def token_auth(request, rtoken):
    # looking if token is valid
    if is_valid(rtoken) is True:
        token = EmailToken.objects.get(token=rtoken)
        # increasing visits count first
        token.increase_visit()
        # adding token to session data, setting 300 sec expiry for test
        request.session['emailtoken'] = rtoken.hex
        request.session.set_expiry(300)
        # token found, redirecting user
        return HttpResponseRedirect(reverse('linksapp:tokenslist'))
    else:
        # token is not valid
        raise Http404()


def tokenslist(request):
    try:
        token_str = request.session['emailtoken']
    except KeyError:
        raise Http404()
    else:
        if is_valid(uuid.UUID(token_str)) is True:
            # User authorised
            # print(uuid.UUID(token_str))
            tokens = EmailToken.objects.all()
            return render(request, 'linksapp/tokens.html', {'tokens': tokens})
        else:
            raise Http404()
