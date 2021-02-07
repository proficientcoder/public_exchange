from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect



def account(request):
    return render(request, 'account/account.html')

def recover(request):
    # TODO
    return render(request, 'account/account.html')