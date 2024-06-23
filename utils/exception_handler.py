from django.http import JsonResponse
from rest_framework.views import exception_handler



def custom_exception_handler(exc, context):
    handlers = {
        # 'ValidationError': handle_generic_error,
        # 'Http404': handle_generic_error,
        # 'PermissionDenied': handle_generic_error,
        'NotAuthenticated': handle_authentication_error
    }

    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    exception_class = exc.__class__.__name__
    
    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    return response

def handle_authentication_error(exc, context, response):
    response.data = {
        'error': 'Please login in to preceed.',
        'status_code': response.status_code
    }
    return response

# def handle_generic_error(exc, context, response):
#     response.data = {
#         'error': 'some error'
#     }
#     return response

