from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .forms import SignupForm
from .models import CustomUser as User


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Generate email verification token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Build email verification URL
            current_site = get_current_site(request)
            verification_url = reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
            verification_url = f"{request.scheme}://{current_site.domain}{verification_url}"

            # Send verification email
            mail_subject = 'Activate your account'
            message = render_to_string('verification_email.html', {
                'user': user,
                'verification_url': verification_url,
            })
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()

            return HttpResponse('Please check your email for the verification link.')

    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


def verify_email(uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return HttpResponse('Email verified successfully. You can now login.')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass

    return HttpResponse('Invalid verification link.')