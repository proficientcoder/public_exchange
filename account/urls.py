from django.urls import path
from django.contrib.auth import views as auth_views

from account import views

urlpatterns = [
    path('', views.account, name='account_'),
    path('recover/', views.recover, name='account_recover'),
    path('deposit', views.deposit, name='account_deposit'),
    path('withdraw', views.withdraw, name='account_withdraw'),
]
