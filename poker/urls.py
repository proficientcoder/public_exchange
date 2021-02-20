from django.urls import path
from django.contrib.auth import views as auth_views

from poker import views as pokerViews

urlpatterns = [
    path('tableState/<int:id>/', pokerViews.pokerTableState, name='pokerTableState'),
    path('createTable/', pokerViews.createTable, name='pokerCreateTable'),
    path('joinTable/<int:id>/', pokerViews.joinTable, name='pokerJoinTable'),
    path('actionFold/<int:id>/', pokerViews.actionFold, name='pokerActionFold'),
    path('actionCall/<int:id>/', pokerViews.actionCall, name='pokerActionCall'),
    path('listMyTables/', pokerViews.listMyTables, name='pokerListMyTables'),
    path('listTables/', pokerViews.listTables, name='pokerListTables'),
]