from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views

import user.views as userViews

urlpatterns = [
    path('', userViews.home, name='userHome'),
    path('register/', userViews.register, name='userRegister'),
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html'), name='userLogin'),
    path('logout/', auth_views.LogoutView.as_view(), name='userLogout'),

    path('createKey/', userViews.createKey, name='userCreateKey'),
    path('deleteKey/<int:id>/', userViews.deleteKey, name='userDeleteKey'),
    path('testKey/', userViews.testKey, name='userTestKey')
]