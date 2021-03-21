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
            log = table.user.username + ' folded'

            index = table.getNextToAct()
            table.lockForUpdate()
            table.setPlayerAction(index, True)
            table.setPlayerCards(index, None)
            table.addLog(log)
            table.save()

    except LookupError:
        print('A lookup error happened!')
        pass

    return JsonResponse({})


def actionCheck(request, id):
    table = pokerClasses.PokerTable(request, id)

    try:
        if table.isRemoteUserAlsoTheNextToAct():
            log = table.user.username + ' checked'

            table.lockForUpdate()
            maxbet = 0

            for i in table.getPlayerRange():
                maxbet = max(maxbet, table.getPlayerNewBet(i))

            index = table.getNextToAct()

            if maxbet != table.getPlayerNewBet(index):
                return JsonResponse({})

            table.setPlayerAction(index, True)
            table.addLog(log)
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

            difference = min(table.getPlayerMoney(i), difference)

            if difference == 0:
                return JsonResponse({'FAIL': 'Nothing to call'})

            log = table.user.username + ' called ' + str(difference)

            table.setPlayerAction(i, True)
            table.setPlayerNewBet(i, maxbet)
            table.setPlayerMoney(i, table.getPlayerMoney(i) - difference)

            table.addLog(log)
            table.save()
    except LookupError:
        print('A lookup error happened!')
        pass

    return JsonResponse({'SUCCESS': 'Called'})


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

            if amount != table.getPlayerMoney(i):   # All-in has no limits
                if amount > table.getPlayerMoney(i):
                    return JsonResponse({'FAIL': 'Dont have that money'})
                if newBet < maxbet + (table.getBlind() / 2):
                    return JsonResponse({'FAIL': 'Bet to low'})

            log = table.user.username + ' raised with ' + str(amount)
            if table.getPlayerMoney(i) == 0:
                log += ' and is allin'

            table.setPlayerAction(i, True)
            table.setPlayerMoney(i, table.getPlayerMoney(i) - amount)
            table.setPlayerNewBet(i, table.getPlayerNewBet(i) + amount)
            table.setLastToAct(table.findPrevPlayerToAct(table.getNextToAct()))

            table.addLog(log)
            table.save()
    except LookupError:
        print('A lookup error happened!')
        pass

    return JsonResponse({})


def tableCreate(request, size):
    if size < 2 or size > 3:
        return JsonResponse({'FAIL': 'Invalid table size'})

    t = pokerModels.PokerTable(size=size)
    t.blind = 10
    t.save()
    return JsonResponse({'SUCCESS': 'Table created'})


def tableDelete(request, id):
    table = pokerClasses.PokerTable(request, id)
    for i in table.getPlayerRange():
        if table.getPlayer(i):
            return JsonResponse({'FAIL': 'Table not empty'})

    table.delete()
    # table.save()
    return JsonResponse({'SUCCESS': 'Table deleted'})


def tableJoin(request, id, buyin):
    user = userFunctions.getUserFromKey(request)
    table = pokerClasses.PokerTable(request, id)

    if buyin < 40 or buyin > 100:
        return JsonResponse({'FAIL': 'Invalid amount'})

    bb = buyin * table.getBlind()
    print(table.getBlind(), bb)

    for i in table.getPlayerRange():
        if table.isPlayer(i) is False:
            table.lockForUpdate()
            table.setPlayer(i, user)
            table.setPlayerMoney(i, bb)
            table.setPlayerJoin(i, True)
            table.save()
            return JsonResponse({'SUCCESS': 'Joined table'})

    return JsonResponse({'FAIL': 'Could not find seat'})


def tableLeave(request, id):
    user = userFunctions.getUserFromKey(request)

    table = pokerClasses.PokerTable(request, id)
    for i in table.getPlayerRange():
        if table.isPlayer(i) is True:
            if table.getPlayer(i) == user:
                table.lockForUpdate()
                table.setPlayerLeave(i, True)
                table.save()

    return JsonResponse({})


def listMyTables(request):
    user = userFunctions.getUserFromKey(request)

    tables = []

    pokerTables = pokerModels.PokerTable.objects.filter(Q(player_0=user.pk) | Q(player_1=user.pk) | Q(player_2=user.pk))
    for table in pokerTables:
        tables.append(table.pk)

    return JsonResponse({'tables': tables})


def listTables(request):
    tables = []

    pokerTables = pokerModels.PokerTable.objects.all()

    if 'size' in request.GET:
        pokerTables = pokerTables.filter(size=request.GET['size'])

    for table in pokerTables:
        count = 0
        for i in range(0, table.size):
            if getattr(table, f'player_{i}') is not None:
                count += 1
        tables.append({'id': table.pk,
                       'size': table.size,
                       'seated': count})

    return JsonResponse({'tables': tables})

