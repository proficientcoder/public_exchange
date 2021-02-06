from django.urls import path
from django.contrib.auth import views as auth_views

from contract import views

urlpatterns = [
    path('register/', views.register, name='create'),

]