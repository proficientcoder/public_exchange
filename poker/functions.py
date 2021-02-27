from poker.pokereval.card import Card
from poker.pokereval.hand_evaluator import HandEvaluator


def cardTranslate(card):
    rank = '23456789TJQKA'.index(card[0])+2
    suit = 'CHDS'.index(card[1])+1

    return Card(rank, suit)
