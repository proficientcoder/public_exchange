from django import forms


what = (
    (1, 'EX1_FIAT_CURRENCY'),
)


class DepositForm(forms.Form):
    amount = forms.IntegerField()
    what = forms.ChoiceField(choices=what)
