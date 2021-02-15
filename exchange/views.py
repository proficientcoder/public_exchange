import global_settings
from django.contrib.auth import login, authenticate
from exchange.forms import TickerCreationForm, DepositFiatForm
from exchange.models import Ticker, Ownership
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'exchange/home.html')


@login_required()
def createTicker(request):
    if request.method == 'POST':
        form = TickerCreationForm(request.POST)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.creator = request.user
            inst.name = global_settings.exchange_id + ':' + inst.name
            inst.save()
            return render(request, 'exchange/createTicker_success.html')
    else:
        form = TickerCreationForm()
    return render(request, 'exchange/createTicker.html', {'form': form})


@login_required()
def depositFiat(request):
    if request.method == 'POST':
        form = DepositFiatForm(request.POST)
        if form.is_valid():
            fiats = Ticker.objects.filter(name='X1:FIAT')
            own = Ownership.objects.filter(ticker=fiats[0])
            if len(own) > 0:
                own = own[0]
                own.amount += form.cleaned_data['amount']
            else:
                own = Ownership.objects.create(ticker=fiats[0], creator=request.user, owner=request.user, amount=form.cleaned_data['amount'])
            own.save()
            return render(request, 'exchange/depositFiat_success.html')
    else:
        form = DepositFiatForm()
    return render(request, 'exchange/depositFiat.html', {'form': form})