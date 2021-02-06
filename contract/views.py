from django.shortcuts import render
from contract.forms import ContractCreationForm
from django.shortcuts import render, redirect

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = ContractCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/contract/register_success.html')
    else:
        form = ContractCreationForm()
    return render(request, 'contract/register.html', {'form': form})