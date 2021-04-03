import time
from user.models import apiKey

cache = {}
timeout = None

def getUserFromKey(request):
    global timeout, cache

    if timeout is None:
        timeout = time.time_ns() + (60 * 10 ** 9)

    if time.time_ns() > timeout:
        timeout = None
        cache = {}

    if 'key' not in request.GET:
        return None

    key = request.GET['key']

    if key in cache:
        u = cache[key]
    else:
        tmp = apiKey.objects.filter(key=key)

        if len(tmp) != 1:
            return None

        u = tmp[0]
        cache[key] = u

    client_ip = get_client_ip(request)
    #print(u.ip, client_ip)
    if u.ip != client_ip:
        return None

    return u.user.username


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip