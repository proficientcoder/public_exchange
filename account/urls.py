from django.urls import path
from django.contrib.auth import views as auth_views

from account import views

urlpatterns = [
    path('', views.account, name='account_'),
    path('recover/', views.recover, name='account_recover'),
    path('register/', views.register, name='account_register'),
    path('login/', auth_views.LoginView.as_view(template_name='account/login.html'), name='account_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='account_logout'),
]
