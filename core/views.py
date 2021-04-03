from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import URLPattern, URLResolver
from collections import namedtuple


def home(request):
    return render(request, 'core/home.html')


def endpoints(request):
    urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])

    def list_urls(lis, acc=None):
        if acc is None:
            acc = []
        if not lis:
            return
        l = lis[0]
        if isinstance(l, URLPattern):
            yield acc + [str(l.pattern)]
        elif isinstance(l, URLResolver):
            yield from list_urls(l.url_patterns, acc + [str(l.pattern)])
        yield from list_urls(lis[1:], acc)

    all_endpoints = []
    for p in list_urls(urlconf.urlpatterns):
        if p[0] != 'admin/':
            url = '/' + ''.join(p)
            ep = {'url': url}
            if url in index:
                ep.update(index[url])
            all_endpoints.append(ep)

    return render(request, 'core/endpoints.html', {'endpoints': all_endpoints})


index = {'/endpoints/': {'type': 'html', 'description': 'Returns a list of all the endpoints', 'link': ''},
         '/poker/listTables/': {'type': 'json', 'description': 'Returns a list of all poker tables', 'link': ''},
         }
