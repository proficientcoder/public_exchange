from django.http import JsonResponse
from poker.models import PokerTable
from poker.pokerTable import ClassPokerTable
from user.models import apiKey
from django.contrib.auth.models import User
from django.db.models import Q
import random


def pokerTableState(request, id):
    key = request.GET['key']
    user = apiKey.objects.filter(key=key)
    cuser = user[0].user
    cuser = cuser.username

    t = PokerTable.objects.filter(id=id)
    t = t[0]

    update(t)

    state = {
        'you': cuser,
        'nrOfSeats': t.size,
        'dealer': t.dealer,
        'blind': t.blind,
        'next_to_act': t.next_to_act,
        'last_to_act': t.last_to_act,
        'players': [],
        'board': t.board,
        'pot': '0',
        'actions': [],
    }

    max_bet = 0
    for i in range(1, t.size+1):
        max_bet = max(max_bet, getattr(t, f'player_{i}_bet'))
        if getattr(t, f'player_{i}') is not None:
            state['players'].append({'name': getattr(t, f'player_{i}').username,
                                     'balance': getattr(t, f'player_{i}_money'),
                                     'last_bet': getattr(t, f'player_{i}_bet'),
                                     'cards': getattr(t, f'player_{i}_cards'),
                                     })
            if getattr(t, f'player_{i}').username != cuser:
                state['players'][-1]['cards'] = ''
        else:
            state['players'].append(None)

    actor_bet = getattr(t, f'player_{t.next_to_act}_bet')

    if max_bet == actor_bet:
        state['actions'].append('CHECK')

    if max_bet > actor_bet:
        state['actions'].append('FOLD')
        state['actions'].append('CALL')

    if max_bet == 0:
        state['actions'].append('BET')

    state['actions'].append('RAISE')


    return JsonResponse(state)


def actionFold(request, id):
    table = ClassPokerTable(request, id)

    try:
        if table.isRemoteUserAlsoTheNextToAct():
            table.setPlayerCards(table.getNextToAct(),
                                 None)
            table.updateOnAction()
    except LookupError:
        print('A lookup error happened!')
        pass

    return JsonResponse({})



def actionCheck(request, id):
    key = request.GET['key']
    user = apiKey.objects.filter(key=key)
    cuser = user[0].user
    cuser = cuser.username

    t = PokerTable.objects.filter(id=id)
    t = t[0]

    if getattr(t, f'player_{t.next_to_act}').username == cuser:
        update(t, didAct=True)

    return JsonResponse({})


def actionCall(request, id):
    key = request.GET['key']
    user = apiKey.objects.filter(key=key)
    cuser = user[0].user
    cuser = cuser.username

    t = PokerTable.objects.filter(id=id)
    t = t[0]

    if getattr(t, f'player_{t.next_to_act}').username == cuser:
        high = 0
        for i in range(1, t.size + 1):
            money = getattr(t, f'player_{i}_bet')
            if money > high:
                high = money

        setattr(t, f'player_{t.next_to_act}_bet', high)

        update(t, didAct=True)

    return JsonResponse({})


def createTable(request):
    t = PokerTable(size=2)
    t.save()
    return JsonResponse({})


def joinTable(request, id):
    u = User.objects.filter(id=1)
    u = u[0]

    t = PokerTable.objects.filter(id=id)
    if len(t) == 1:
        t = t[0]
        if t.player_1 == None:
            t.player_1 = u
            t.save()
        elif t.player_2 == None:
            t.player_2 = u
            t.save()

    return JsonResponse({})


def listMyTables(request):
    key = request.GET['key']
    user = apiKey.objects.filter(key=key)
    cuser = user[0].user
    cuser = cuser.pk

    tables = []

    u = User.objects.filter(id=cuser)
    u = u[0]

    pt = PokerTable.objects.filter(Q(player_1=u) | Q(player_2=u))
    for p in pt:
        tables.append(p.pk)

    return JsonResponse({'tables': tables})


def listTables(request):
    tables = []

    u = User.objects.filter(id=1)
    u = u[0]

    pt = PokerTable.objects.all()
    for p in pt:
        tables.append({'id': p.pk,
                       'size': p.size})

    return JsonResponse({'tables': tables})
