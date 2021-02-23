
from user.models import apiKey

def getUserFromKey(request):
    if 'key' not in request.GET:
        raise LookupError   # Key is not specified

    key = request.GET['key']
    tmp = apiKey.objects.filter(key=key)

    if len(tmp) != 1:
        raise LookupError   # The API key could not be found

    return tmp[0].user