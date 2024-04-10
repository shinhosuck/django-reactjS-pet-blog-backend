# excepts = {
#     'ValidationError': handle_generic_error,
#     'Http404': handle_generic_error,
#     'PermissionDenied': handle_generic_error,
#     'NotAuthenticated': _handle_authentication_error
# }


def fetch_host(request):
    if request.get_host() == '127.0.0.1:8000':
        return f'http://{request.get_host()}'
    return f'https://{request.get_host()}'


