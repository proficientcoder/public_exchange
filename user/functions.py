
from user.models import apiKey

def getUserFromKey(request):
    if 'key' not in request.GET:
        return None

    key = request.GET['key']
    tmp = apiKey.objects.filter(key=key)

    if len(tmp) != 1:
        return None

    return tmp[0].user