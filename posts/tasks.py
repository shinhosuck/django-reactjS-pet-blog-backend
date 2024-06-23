from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string 
from django.conf import settings


from_email = settings.EMAIL_HOST_USER


@shared_task
def send_email(email=None, full_name=None, subject_type=None, queue='task'):
    
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

    return 'Email successfully sent'


