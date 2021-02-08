from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from core.forms import DepositForm
from core.models import Contract, Ownership


def account(request):
    return render(request, 'account/account.html')


def recover(request):
    return render(request, 'core/dummy.html')


def deposit(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DepositForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            amount = form.cleaned_data['amount']
            what = form.cleaned_data['what']
            contract = Contract.objects.filter(pk=what)
            contract_pk = contract[0]
            created_by = request.user
            co = Ownership.objects.filter(contract_id=what)
            if len(co) > 0:
                o = co[0]
                o.amount += amount
            else:
                o = Ownership(contract=contract_pk,
                              created_by=created_by,
                              owned_by=created_by,
                              amount=amount)
            o.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return render(request, 'account/deposit_success.html')
    else:
        form = DepositForm()

    return render(request, 'account/deposit.html', {'form': form})


def withdraw(request):
    return render(request, 'core/dummy.html')