import uuid
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from user.models import apiKey
from django.contrib.auth.decorators import login_required

import user.functions as userFunctions


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            inst = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return render(request, 'user/register_success.html')
    else:
        form = UserCreationForm()
    return render(request, 'user/register.html', {'form': form})


@login_required()
def home(request):
    keys = apiKey.objects.all().filter(user=request.user)
    return render(request, 'user/home.html', {'keys': keys})


@login_required()
def createKey(request):
    client_ip = userFunctions.get_client_ip(request)

    key = apiKey(user=request.user, key=str(uuid.uuid4()), ip=client_ip)
    key.save()

    return redirect('userHome')


@login_required()
def deleteKey(request, id):
    keys = apiKey.objects.all().filter(user=request.user, id=id)
    if len(keys) == 1:
        k = keys[0]
        k.delete()

    return redirect('userHome')


def testKey(request):
    try:
        user = userFunctions.getUserFromKey(request)
    except LookupError:
        return JsonResponse({'ERR': 'LookupError'})

    if user:
        return JsonResponse({'username': user})
    else:
        return JsonResponse({'ERR': 'LookupError'})
