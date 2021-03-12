from django.urls import path
from django.contrib.auth import views as auth_views

import poker.views as pokerViews


urlpatterns = [
    path('tableState/<int:id>/', pokerViews.pokerTableState, name='pokerTableState'),
    path('tableCreate/', pokerViews.tableCreate, name='pokerTableCreate'),
    path('tableJoin/<int:id>/', pokerViews.tableJoin, name='pokerTableJoin'),
    path('tableDelete/<int:id>/', pokerViews.tableDelete, name='pokerTableDelete'),
    path('tableLeave/<int:id>/', pokerViews.tableLeave, name='pokerTableLeave'),

    path('actionFold/<int:id>/', pokerViews.actionFold, name='pokerActionFold'),
    path('actionCall/<int:id>/', pokerViews.actionCall, name='pokerActionCall'),
    path('actionRaise/<int:id>/<int:amount>/', pokerViews.actionRaise, name='pokerActionRaise'),
    path('actionCheck/<int:id>/', pokerViews.actionCheck, name='pokerActionCheck'),

    path('listMyTables/', pokerViews.listMyTables, name='pokerListMyTables'),
    path('listTables/', pokerViews.listTables, name='pokerListTables'),
]