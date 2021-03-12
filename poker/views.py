from django.http import JsonResponse
from django.db.models import Q

import poker.models as pokerModels
import poker.classes as pokerClasses
import user.functions as userFunctions


def pokerTableState(request, id):
    table = pokerClasses.PokerTable(request, id)

    table.user = userFunctions.getUserFromKey(request)

    table.updateTableState()

    state = table.getPokerTableState()
    return JsonResponse(state)



def actionFold(request, id):
    table = pokerClasses.PokerTable(request, id)

    try:
        if table.isRemoteUserAlsoTheNextToAct():
            index = table.getNextToAct()
            table.lockForUpdate()
            table.setPlayerAction(index, True)
            table.setPlayerCards(index, None)
            table.save()

    except LookupError:
        print('A lookup error happened!')
        pass

    return JsonResponse({})


def actionCheck(request, id):
    table = pokerClasses.PokerTable(request, id)

    try:
        if table.isRemoteUserAlsoTheNextToAct():
            table.lockForUpdate()
            maxbet = 0

            for i in table.getPlayerRange():
                maxbet = max(maxbet, table.getPlayerNewBet(i))

            index = table.getNextToAct()

            if maxbet != table.getPlayerNewBet(index):
                return JsonResponse({})

            table.setPlayerAction(index, True)
            table.save()
    except LookupError:
        print('A lookup error happened!')
        pass

    return JsonResponse({})


def actionCall(request, id):
    table = pokerClasses.PokerTable(request, id)

    try:
        if table.isRemoteUserAlsoTheNextToAct():
            table.lockForUpdate()
            maxbet = 0

            for i in table.getPlayerRange():
                maxbet = max(maxbet, table.getPlayerNewBet(i))

            # Move the money
            i = table.getNextToAct()
            difference = maxbet - table.getPlayerNewBet(i)

            if difference > table.getPlayerMoney(i) or difference == 0:
                return JsonResponse({})

            table.setPlayerAction(i, True)
            table.setPlayerNewBet(i, maxbet)
            table.setPlayerMoney(i, table.getPlayerMoney(i) - difference)

            table.save()
    except LookupError:
        print('A lookup error happened!')
        pass

    return JsonResponse({})


def actionRaise(request, id, amount):
    table = pokerClasses.PokerTable(request, id)

    try:
        if table.isRemoteUserAlsoTheNextToAct():
            table.lockForUpdate()
            maxbet = 0

            for i in table.getPlayerRange():
                maxbet = max(maxbet, table.getPlayerNewBet(i))

            # Move the money
            i = table.getNextToAct()
            newBet = table.getPlayerNewBet(i) + amount
            print(newBet, amount)

            if amount != table.getPlayerMoney(i):   # All-in has no limits
                if amount > table.getPlayerMoney(i) or newBet < maxbet + (table.getBlind() / 2):
                    return JsonResponse({})

            print('raise')
            table.setPlayerAction(i, True)
            table.setPlayerMoney(i, table.getPlayerMoney(i) - amount)
            table.setPlayerNewBet(i, table.getPlayerNewBet(i) + amount)
            table.setLastToAct(table.findPrevPlayerToAct(table.getNextToAct()))

            table.save()
    except LookupError:
        print('A lookup error happened!')
        pass

    return JsonResponse({})


def tableCreate(request):
    t = pokerModels.PokerTable(size=2)
    t.save()
    return JsonResponse({})


def tableDelete(request, id):
    # TODO check if table is empty
    tmp = pokerModels.PokerTable.objects.filter(id=id)
    tmp.delete()

    return JsonResponse({})


def tableJoin(request, id):
    user = userFunctions.getUserFromKey(request)

    table = pokerClasses.PokerTable(request, id)
    for i in table.getPlayerRange():
        if table.isPlayer(i) is False:
            table.setPlayer(i, user)
            table.setPlayerMoney(i, 50)     # TODO Move money
            table.save()
            return JsonResponse({})

    return JsonResponse({})


def tableLeave(request, id):
    user = userFunctions.getUserFromKey(request)

    table = pokerClasses.PokerTable(request, id)
    for i in table.getPlayerRange():
        if table.isPlayer(i) is True:
            if table.getPlayer(i) == user:
                table.setPlayer(i, None)
                table.setPlayerMoney(i, 0) # TODO Move money
                table.setPlayerCards(i, None)

                table.save()

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
        count = 0
        for i in range(1, table.size+1):
            if getattr(table, f'player_{i}') is not None:
                count += 1
        tables.append({'id': table.pk,
                       'size': table.size,
                       'seated': count})

    return JsonResponse({'tables': tables})

