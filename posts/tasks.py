from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string 
from django.conf import settings


from_email = settings.EMAIL_HOST_USER


@shared_task
def subscribe(email, full_name, subject_type, queue='task'):
    
    context = {
        'full_name': full_name,
        'email': email
    }

    html_body = render_to_string('posts/subscribe.html', context=context)
    message = EmailMultiAlternatives(
        subject = subject_type,
        body = '',
        from_email = from_email,
        to = [email]
    )
    message.attach_alternative(html_body, 'text/html')
    message.send(fail_silently=False)

    return 'Email successfully sent'


@shared_task
def contact_us(email, subject_type, queue='task'):
    
    context = {
        'email': email
    }

    html_body = render_to_string('posts/contact-us.html', context=context)
    message = EmailMultiAlternatives(
        subject = subject_type,
        body = '',
        from_email = from_email,
        to = [email]
    )
    message.attach_alternative(html_body, 'text/html')
    message.send(fail_silently=False)

    return 'Email successfully sent'


@shared_task
def new_comment(email, username, post, comment, url_to_comment, parent_comment=None, queue='task'):
    
    context = {
        'username':username,
        'post':post,
        'comment':comment,
        'parent_comment':parent_comment,
        'url_to_comment':url_to_comment
    }

    html_body = render_to_string('posts/new-comment.html', context=context)
    message = EmailMultiAlternatives(
        subject = 'New Comment',
        body = '',
        from_email = from_email,
        to = [email]
    )
    message.attach_alternative(html_body, 'text/html')
    message.send(fail_silently=False)

    return 'Email successfully sent'