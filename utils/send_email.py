from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string 
from django.conf import settings
# from django.template import Template

from_email = settings.EMAIL_HOST_USER

# def send_email(request, subject_type=None, email=None, full_name=None):

    
#     context = {
#         'full_name': full_name,
#         'email': email
#     }
#     html_body = render_to_string('posts/send_email.html', context=context)
#     message = EmailMultiAlternatives(
#         subject = subject_type,
#         body = '',
#         from_email = from_email,
#         to = [email]
#     )
#     message.attach_alternative(html_body, 'text/html')
#     message.send(fail_silently=False)

#     return 'Message sent!'


def subscribe(email, full_name, subject_type):
    
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


def contact_us(email, subject_type):
    
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


def new_comment(email, username, post, comment, url_to_comment, parent_comment=None):
    
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

