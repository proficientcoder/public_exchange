from django import forms

from exchange.models import Ticker


class TickerCreationForm(forms.ModelForm):
    class Meta:
        model = Ticker
        fields = ['name']


class DepositFiatForm(forms.Form):
    amount = forms.IntegerField(min_value=1, max_value=1000)
