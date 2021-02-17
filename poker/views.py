from django.http import JsonResponse
from poker.models import PokerTable
from django.contrib.auth.models import User
from django.db.models import Q


# Create your views here.
def pokerTableState(request, id):
    t = PokerTable.objects.filter(id=id)
    t = t[0]

    state = {
        'nrOfSeats': t.size,
        'players': [],
        'board': [None, None, None, None, None],
        'pot': '0',
        'actions': [],
    }

    if t.player_1 is not None:
        state['players'].append({'name': t.player_1.username,
                                 'balance': '10.0',
                                 'is_dealer': False,
                                 'last_bet': '',
                                 'cards': ['A♠', 'J♥'],
                                 })
    else:
        state['players'].append(None)

    if t.player_2 is not None:
        state['players'].append({'name': t.player_2.username,
                                 'balance': '10.0',
                                 'is_dealer': False,
                                 'last_bet': '',
                                 'cards': ['A♦', 'J♣'],
                                 })
    else:
        state['players'].append(None)

    return JsonResponse(state)


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
    tables = []

    u = User.objects.filter(id=1)
    u = u[0]

    pt = PokerTable.objects.filter(Q(player_1=u) | Q(player_2=u))
    for p in pt:
        tables.append(p.pk)

    return JsonResponse({'tables': tables})
