from django import forms
from contract.models import Contract



class ContractCreationForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['descriptive_name',
                  'legal',
                  'unique',
                  'website',
                  'expiry_date',
                  'underlying_value']