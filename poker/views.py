from django.http import JsonResponse
from django.db.models import Q

import poker.models as pokerModels
import poker.classes as pokerClasses
import user.functions as userFunctions


def pokerTableState(request, id):
    user = userFunctions.getUserFromKey(request)
    table = pokerClasses.PokerTable(request, id)

    table.updateWithoutAction()

    state = {
        'you': user.username,
        'nrOfSeats': table.getSize(),
        'dealer': table.getDealer(),
        'blind': table.getBlind(),
        'next_to_act': table.getNextToAct(),
        'last_to_act': table.getLastToAct(),
        'players': [None],  # Add single element for client offset
        'board': table.getBoardCards(),
        'pot': table.getPot(),
        'actions': [],
    }

    max_bet = 0
    for i in table.getPlayerRange():
        max_bet = max(max_bet, table.getPlayerBet(i))
        if table.isPlayer(i):
            state['players'].append({'name': table.getPlayer(i).username,
                                     'balance': table.getPlayerMoney(i),
                                     'last_bet': table.getPlayerBet(i),
                                     'cards': table.getPlayerCards(i),
                                     })
            if table.getPlayer(i) != user:
                state['players'][-1]['cards'] = ''
        else:
            state['players'].append(None)

    actor_bet = table.getPlayerBet(table.getNextToAct())

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
    table = pokerClasses.PokerTable(request, id)

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
    table = pokerClasses.PokerTable(request, id)

    try:
        if table.isRemoteUserAlsoTheNextToAct():
            table.updateOnAction()
    except LookupError:
        print('A lookup error happened!')
        pass

    return JsonResponse({})


def actionCall(request, id):
    table = pokerClasses.PokerTable(request, id)

    try:
        if table.isRemoteUserAlsoTheNextToAct():
            highestBet = 0
            for i in table.getPlayerRange():
                money = table.getPlayerBet(i)
                if money > highestBet:
                    highestBet = money

            # Move the money
            i = table.getNextToAct()
            difference = highestBet - table.getPlayerBet(i)
            table.setPlayerBet(i, highestBet)
            table.setPlayerMoney(i, table.getPlayerMoney(i) - difference)

            table.updateOnAction()
    except LookupError:
        print('A lookup error happened!')
        pass

    return JsonResponse({})


def createTable(request):
    t = pokerModels.PokerTable(size=2)
    t.save()
    return JsonResponse({})


def joinTable(request, id):
    user = userFunctions.getUserFromKey(request)

    table = pokerClasses.PokerTable(request, id)
    for i in table.getPlayerRange():
        if table.isPlayer(i) is False:
            table.setPlayer(user)
            table.save()
            return

    return JsonResponse({})


def listMyTables(request):
    user = userFunctions.getUserFromKey(request)

    tables = []

    pokerTables = pokerModels.PokerTable.objects.filter(Q(player_1=user.pk) | Q(player_2=user.pk))
    for table in pokerTables:
        tables.append(table.pk)

    return JsonResponse({'tables': tables})


def listTables(request):
    tables = []

    pokerTables = pokerModels.PokerTable.objects.all()
    for table in pokerTables:
        tables.append({'id': table.pk,
                       'size': table.size})

    return JsonResponse({'tables': tables})

