import global_settings
from django.contrib.auth import login, authenticate
from exchange.forms import TickerCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'exchange/home.html')


@login_required()
def createTicker(request):
    if request.method == 'POST':
        form = TickerCreationForm(request.POST)
        if form.is_valid():
            inst = form.save()
            inst.descriptive_name = global_settings.exchange_id + ':' + inst.descriptive_name
            inst.created_by = request.user
            inst.save()
            return render(request, 'exchange/createTicker_success.html')
    else:
        form = TickerCreationForm()
    return render(request, 'exchange/createTicker.html', {'form': form})