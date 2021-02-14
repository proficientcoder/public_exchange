from django import forms

from exchange.models import Ticker


class TickerCreationForm(forms.ModelForm):
    class Meta:
        model = Ticker
        fields = ['name']