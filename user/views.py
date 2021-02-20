import uuid
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from user.models import apiKey
from django.contrib.auth.decorators import login_required


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
def createKey(request):
    key = apiKey(user=request.user, key=str(uuid.uuid4()))
    key.save()

    return JsonResponse({})
