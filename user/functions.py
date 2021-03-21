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
        return cache[key]

    tmp = apiKey.objects.filter(key=key)

    if len(tmp) != 1:
        return None

    u = tmp[0].user.username
    cache[key] = u

    return u