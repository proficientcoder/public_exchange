from django.urls import path
from django.contrib.auth import views as auth_views

from exchange import views as exchangeViews

urlpatterns = [
    path('', exchangeViews.home, name='exchangeHome'),
    path('createTicker/', exchangeViews.createTicker, name='exchangeCreateTicker'),
    path('depositFiat/', exchangeViews.depositFiat, name='exchangeDepositFiat'),
]