from django.urls import path
from django.contrib.auth import views as auth_views

from exchange import views as exchangeViews

urlpatterns = [
    path('', exchangeViews.home, name='exchangeHome'),
    path('createTicker/', exchangeViews.createTicker, name='exchangeCreateTicker'),
    path('depositFiat/', exchangeViews.depositFiat, name='exchangeDepositFiat'),
    path('viewTickers/', exchangeViews.viewTickers, name='exchangeViewTickers'),
    path('viewPairs/', exchangeViews.viewPairs, name='exchangeViewPairs'),
    path('viewOrders/', exchangeViews.viewOrders, name='exchangeViewOrders'),
    path('viewOwnerships/', exchangeViews.viewOwnerships, name='exchangeViewOwnerships'),
]