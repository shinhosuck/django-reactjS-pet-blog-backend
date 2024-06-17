from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string 
from django.conf import settings
from django.template import Template

from_email = settings.EMAIL_HOST_USER

def send_email(request, subject_type=None, email=None, full_name=None):

    
    context = {
        'full_name': full_name,
        'email': email
    }
    html_body = render_to_string('posts/send_email.html', context=context)
    message = EmailMultiAlternatives(
        subject = subject_type,
        body = '',
        from_email = from_email,
        to = [email]
    )
    message.attach_alternative(html_body, 'text/html')
    message.send(fail_silently=False)

    return 'Message sent!'


