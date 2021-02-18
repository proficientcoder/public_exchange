from django.http import JsonResponse
from poker.models import PokerTable
from django.contrib.auth.models import User
from django.db.models import Q
import random


def createDeck():
    deck = []
    cards = '23456789TJQKA'
    suits = '♠♥♦♣'

    for c in cards:
        for s in suits:
            deck.append(c + s)

    random.shuffle(deck)
    deck = ''.join(deck)
    return deck


def nextPlayer(t, pos):
    pos += 1
    if pos > t.size:
        pos = 1
    while getattr(t, f'player_{pos}') is None:
        pos += 1
        if pos > t.size:
            pos = 1

    return pos


def update(t):
    if t.state == 0:
        nrActive = 0
        for i in range(1, t.size+1):
            if getattr(t, f'player_{i}') is not None:
                nrActive += 1

        if nrActive >= 2:
            t.state = 1
            t.dealer = nextPlayer(t, t.dealer)
            t.deck = createDeck()
            for i in range(1, t.size + 1):
                if getattr(t, f'player_{i}') is not None:
                    r = t.deck[0:4]
                    t.deck = t.deck[4:]
                    setattr(t, f'player_{i}_cards', r)

            sb_pos = nextPlayer(t, t.dealer)
            setattr(t, f'player_{sb_pos}_bet', t.blind / 2)

            bb_pos = nextPlayer(t, sb_pos)
            setattr(t, f'player_{bb_pos}_bet', t.blind)

            t.next_to_act = nextPlayer(t, bb_pos)
            t.last_to_act = bb_pos

            t.save()




def pokerTableState(request, id):
    t = PokerTable.objects.filter(id=id)
    t = t[0]

    update(t)

    state = {
        'nrOfSeats': t.size,
        'dealer': t.dealer,
        'blind': t.blind,
        'next_to_act': t.next_to_act,
        'last_to_act': t.last_to_act,
        'players': [],
        'board': [None, None, None, None, None],
        'pot': '0',
        'actions': [],
    }

    max_bet = 0
    for i in range(1, t.size+1):
        max_bet = max(max_bet, getattr(t, f'player_{i}_bet'))
        if getattr(t, f'player_{i}') is not None:
            state['players'].append({'name': getattr(t, f'player_{i}').username,
                                     'balance': '50.0',
                                     'last_bet': getattr(t, f'player_{i}_bet'),
                                     'cards': getattr(t, f'player_{i}_cards'),
                                     })
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
        else:
            state['actions'].append('RAISE')


    return JsonResponse(state)


def actionFold(request, id):
    t = PokerTable.objects.filter(id=id)
    t = t[0]

    setattr(t, f'player_{t.next_to_act}_cards', None)
    t.save()
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
    tables = []

    u = User.objects.filter(id=1)
    u = u[0]

    pt = PokerTable.objects.filter(Q(player_1=u) | Q(player_2=u))
    for p in pt:
        tables.append(p.pk)

    return JsonResponse({'tables': tables})
