from django.http import JsonResponse
from rest_framework import status



def error_404(request, exception):
    message = {
        'error': 'Page not found. Please check your url and try again.',
        'status_code': 404
    }
    response = JsonResponse(data=message)
    response.status_code = 404
    return response


def error_500(request):
    print('hello world')
    message = {
        'error': 'Server error. Please try again later.',
        'status_code': 500
    }
    response = JsonResponse(data=message)
    response.status_code = 500
    return response