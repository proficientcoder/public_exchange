from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            inst = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return render(request, 'account/register_success.html')
    else:
        form = UserCreationForm()
    return render(request, 'account/register.html', {'form': form})


def account(request):
    return render(request, 'account/account.html')


def recover(request):
    # Recoverform
    return render(request, 'account/account.html')