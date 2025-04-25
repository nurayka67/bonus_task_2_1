# accounts/views.py
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model


# Регистрация пользователя
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(username=username, email=email, password=password, is_active=False)

        # Генерация токена для подтверждения email
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(user.pk.encode())

        # Отправка email для подтверждения
        mail_subject = 'Confirm your email address'
        message = render_to_string('accounts/confirmation_email.html', {
            'user': user,
            'domain': get_current_site(request).domain,
            'uid': uid,
            'token': token,
        })
        send_mail(mail_subject, message, 'from@example.com', [email])

        return HttpResponse('Please confirm your email to activate your account.')
    return render(request, 'accounts/register.html')


# Подтверждение email
def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        return HttpResponse('Invalid confirmation link.')

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Your email has been confirmed. You can now log in.')
    else:
        return HttpResponse('Invalid token or expired link.')
