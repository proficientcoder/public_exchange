import socket
from django.shortcuts import render
from contract.forms import ContractCreationForm
from django.shortcuts import render, redirect

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = ContractCreationForm(request.POST)
        if form.is_valid():
            inst = form.save()
            inst.descriptive_name = socket.gethostname() + '-' + inst.descriptive_name
            inst.created_by = request.user
            inst.save()
            return render(request, 'contract/register_success.html')
    else:
        form = ContractCreationForm()
    return render(request, 'contract/register.html', {'form': form})



def contract(request):
    return render(request, 'contract/contract.html')
