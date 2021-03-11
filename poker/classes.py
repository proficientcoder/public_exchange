import random
import pytz
import time
import datetime
from django.conf import settings
from django.utils.timezone import make_aware
from user.models import apiKey
from django.contrib.auth.models import User

from poker.pokereval.card import Card
from poker.pokereval.hand_evaluator import HandEvaluator

import poker.models as pokerModels
import user.functions as userFunctions
import poker.functions as pokerFunctions


class TableStates:
    RESET = -1
    NOGAME = 0
    SETUP = 10000
    SETUP_DEAL = 11000
    SETUP_BUTTON = 12000
    SETUP_SMALL_BLIND = 13000
    SETUP_BIG_BLIND = 14000
    ROUNDS = 20000
    ROUNDS_DEAL = 21000
    ROUNDS_BETTING = 22000
    ROUNDS_LAST_MAN_STANDING = 23000
    SHOWDOWN = 30000


class PokerTable:
    db = None
    user = None

    def __init__(self, request, id):
        tmp = pokerModels.PokerTable.objects.filter(id=id)
        if len(tmp) != 1:
            raise LookupError   # The table id could not be found

        self.db = tmp[0]

        if 'key' in request.GET:
            self.user = userFunctions.getUserFromKey(request)

    def lockForUpdate(self):
        tmp = pokerModels.PokerTable.objects.select_for_update(nowait=True).filter(id=self.db.pk)
        if len(tmp) != 1:
            raise LookupError   # The table id could not be found

        self.db = tmp[0]

    def save(self):
        self.db.save()

    def getSize(self):
        return int(self.db.size)

    def getPlayerName(self, nr):
        return getattr(self.db, f'player_{nr}').username

    def setPlayerCards(self, nr, what):
        setattr(self.db, f'player_{nr}_cards', what)

    def getPlayerCards(self, nr):
        return getattr(self.db, f'player_{nr}_cards')

    def setPlayerNewBet(self, nr, what):
        setattr(self.db, f'player_{nr}_new_bet', what)

    def getPlayerNewBet(self, nr):
        return float(getattr(self.db, f'player_{nr}_new_bet'))

    def setPlayerPrevBet(self, nr, what):
        setattr(self.db, f'player_{nr}_prev_bet', what)

    def getPlayerPrevBet(self, nr):
        return float(getattr(self.db, f'player_{nr}_prev_bet'))

    def setPlayerMoney(self, nr, what):
        setattr(self.db, f'player_{nr}_money', what)

    def getPlayerMoney(self, nr):
        return float(getattr(self.db, f'player_{nr}_money'))

    def getNextToAct(self):
        return self.db.next_to_act

    def setNextToAct(self, what):
        self.db.next_to_act = what

    def getLastToAct(self):
        return self.db.last_to_act

    def setLastToAct(self, what):
        self.db.last_to_act = what

    def getPlayerRange(self):
        return range(0, self.db.size)

    def getNrOfPlayersWithCards(self):
        c = 0
        for i in self.getPlayerRange():
            if self.getPlayerCards(i):
                c += 1
        return c

    def getBoardCards(self):
        return self.db.board

    def setBoardCards(self, what):
        self.db.board = what

    def getPot(self):
        return float(self.db.pot)

    def drawCardFromDeck(self):
        card = self.db.deck[0:2]
        self.db.deck = self.db.deck[2:]
        return card

    def getDealer(self):
        return self.db.dealer

    def setDealer(self, what):
        self.db.dealer = what

    def getState(self):
        return self.db.state

    def setState(self, what):
        self.db.state = what

    def getBlind(self):
        return float(self.db.blind)

    def getPlayer(self, nr):
        return getattr(self.db, f'player_{nr}')

    def setPlayer(self, nr, what):
        setattr(self.db, f'player_{nr}', what)

    def getPlayerAction(self, nr):
        return getattr(self.db, f'player_{nr}_action')

    def setPlayerAction(self, nr, what):
        setattr(self.db, f'player_{nr}_action', what)

    def setShowDownCounter(self):
        n = datetime.datetime.utcnow()
        now = make_aware(n)
        self.db.showDownCounter = now

    def getShowDownTimer(self):
        return self.db.showDownCounter

    # Helpers

    def createDeck(self):
        deck = []
        cards = '23456789TJQKA'
        suits = 'SHDC'  # ♠♥♦♣

        for c in cards:
            for s in suits:
                deck.append(c + s)

        random.shuffle(deck)
        self.db.deck = ''.join(deck)

    def isPlayerReadyToEnter(self, nr):
        return getattr(self.db, f'player_{nr}') is not None

    def isPlayer(self, nr):
        if self.getPlayer(nr) is None:
            return False
        else:
            return True

    def nextPlayerReadyToEnter(self, position):
        position += 1
        if position > self.db.size:
            position = 1
        while self.isPlayerReadyToEnter(position) is False:
            position += 1
            if position > self.db.size:
                position = 1

        return position

    def isRemoteUserAlsoTheNextToAct(self):
        return self.getPlayerName(self.getNextToAct()) == self.user.username

    def didNextToActRaise(self):
        myBet = self.getPlayerBet(self.getNextToAct())

        for i in self.getPlayerRange():
            bet = self.getPlayerBet(i)
            if bet == myBet and i != self.getNextToAct():
                return False

        return True

    def isPlayerAbleToAct(self, position):     # Can the player act?
        if self.getPlayer(position) is not None:
            if self.getPlayerCards(position) is not None:
                if self.getPlayerMoney(position) != 0:
                    return True

        return False

    def isPlayerInGame(self, position):     # Can the player act?
        if self.getPlayer(position) is not None:
            if self.getPlayerCards(position) is not None:
                return True

        return False

    def findNextPlayerToAct(self, position):    # Next player that can act
        start = position

        c = True
        while c:
            position += 1
            if position > self.db.size - 1:
                position = 0

            c = not self.isPlayerAbleToAct(position)
            if position == start:   # Prevent loop
                c = False

        return position

    def findPrevPlayerToAct(self, position):
        start = position

        c = True
        while c:
            position -= 1
            if position < 0:
                position = self.db.size - 1

            c = not self.isPlayerAbleToAct(position)
            if position == start:  # Prevent loop
                c = False

        return position

    # The big stuff

    def getPokerTableState(self):
        state = {
            'nrOfSeats': self.getSize(),
            'dealer': self.getDealer(),
            'blind': self.getBlind(),
            'next_to_act': self.getNextToAct(),
            'last_to_act': self.getLastToAct(),
            'players': [],
            'board': self.getBoardCards(),
            'actions': [],
        }

        if self.user != None:
            state['you'] = self.user.username

        max_bet = 0
        for i in self.getPlayerRange():
            max_bet = max(max_bet, self.getPlayerNewBet(i))

        for i in self.getPlayerRange():
            if self.isPlayer(i):
                state['players'].append({'id': i,
                                         'name': self.getPlayer(i).username,
                                         'balance': self.getPlayerMoney(i),
                                         'new_bet': self.getPlayerNewBet(i),
                                         'prev_bet': self.getPlayerPrevBet(i),
                                         'cards': '',
                                         })
                if self.user != None:
                    if self.getPlayer(i) == self.user or self.getState() == TableStates.SHOWDOWN:
                        state['players'][-1]['cards'] = self.getPlayerCards(i)

                    if i == self.getNextToAct() and self.getPlayer(i) == self.user and self.getState() == TableStates.ROUNDS_BETTING:
                        actor_bet = self.getPlayerNewBet(self.getNextToAct())

                        if max_bet == actor_bet:
                            state['actions'].append('CHECK')

                        if max_bet > actor_bet:
                            state['actions'].append('FOLD')
                            state['actions'].append('CALL')

                        if max_bet == 0:
                            state['actions'].append('BET')

                        state['actions'].append('RAISE')

            else:
                state['players'].append(None)

        return state


    def stateReset(self):
        n = datetime.datetime.utcnow()
        now = make_aware(n)

        self.db.size = 2
        self.db.state = -1
        self.db.dealer = 0
        self.db.next_to_act = 0
        self.db.last_to_act = 0
        self.db.blind = 10
        self.db.deck = None
        self.db.board = None
        self.db.eventTimer = now
        self.db.updateTimer = None
        self.db.player_0_cards = None
        self.db.player_0_new_bet = 0
        self.db.player_0_prev_bet = 0
        self.db.player_0_money = 50
        self.db.player_0_action = -1
        self.db.player_1_cards = None
        self.db.player_1_new_bet = 0
        self.db.player_1_prev_bet = 0
        self.db.player_1_money = 50
        self.db.player_1_action = -1
        self.db.player_2_cards = None
        self.db.player_2_new_bet = 0
        self.db.player_2_prev_bet = 0
        self.db.player_2_money = 50
        self.db.player_2_action = -1

        self.db.state = TableStates.NOGAME

        return True


    def stateNoGame(self):
        nrActive = 0
        for i in self.getPlayerRange():
            if self.isPlayerReadyToEnter(i):
                nrActive += 1

        if nrActive >= 2:
            self.setState(TableStates.SETUP)

        return False

    def stateSetup(self):
        self.createDeck()
        self.setState(TableStates.SETUP_BUTTON)

        return True


    def stateSetupButton(self):
        self.setDealer(self.findNextPlayerToAct(self.getDealer()))
        self.setState(TableStates.SETUP_DEAL)

        return True


    def stateSetupDeal(self):
        # Deal cards
        for i in self.getPlayerRange():
            if self.isPlayerReadyToEnter(i):
                card1 = self.drawCardFromDeck()
                card2 = self.drawCardFromDeck()
                self.setPlayerCards(i, card1 + card2)

        self.setNextToAct(self.findNextPlayerToAct(self.getDealer()))

        self.setState(TableStates.SETUP_SMALL_BLIND)

        return True

    def stateSetupSmallBlind(self):
        sb_pos = self.getNextToAct()
        amount = int(self.getBlind() / 2)
        self.setPlayerNewBet(sb_pos, amount)
        self.setPlayerMoney(sb_pos, self.getPlayerMoney(sb_pos) - amount)
        self.setNextToAct(self.findNextPlayerToAct(self.getNextToAct()))
        self.setState(TableStates.SETUP_BIG_BLIND)

        return True

    def stateSetupBigBlind(self):
        bb_pos = self.getNextToAct()
        amount = self.getBlind()
        self.setPlayerNewBet(bb_pos, amount)
        self.setPlayerMoney(bb_pos, self.getPlayerMoney(bb_pos) - amount)
        self.setNextToAct(self.findNextPlayerToAct(self.getNextToAct()))
        self.setLastToAct(self.findPrevPlayerToAct(self.getNextToAct()))

        self.setState(TableStates.ROUNDS_BETTING)   # Go straight into the betting part

        return False

    def stateRoundsBetting(self):
        howManyCanAct = 0
        for i in self.getPlayerRange():
            if self.isPlayerAbleToAct(i):
                howManyCanAct += 1

        if howManyCanAct < 2:
            if len(self.getBoardCards()) < 10:
                self.setState(TableStates.ROUNDS)
            else:
                self.setState(TableStates.SHOWDOWN)

            return True

        howManyInGame = 0
        for i in self.getPlayerRange():
            if self.isPlayerInGame(i):
                howManyInGame += 1

        if howManyInGame < 2:
            self.setState(TableStates.ROUNDS_LAST_MAN_STANDING)
            return True

        # Did player act
        didAct = self.getPlayerAction(self.getNextToAct())
        if didAct:
            self.setPlayerAction(self.getNextToAct(), False)
            self.db.eventTimer = None

            if self.getNextToAct() == self.getLastToAct():
                pass      # TODO Done with round

            self.setNextToAct(self.findNextPlayerToAct(self.getNextToAct()))

        # Did time run out
        n = datetime.datetime.utcnow()
        now = make_aware(n)
        if self.db.eventTimer is None:
            self.db.eventTimer = now

        if now < self.db.eventTimer + datetime.timedelta(seconds=15):
            return False

        self.setPlayer(self.getNextToAct(), None)   # TODO refund money
        self.setNextToAct(self.findNextPlayerToAct(self.getNextToAct()))
        self.db.eventTimer = now
        return False


    def updateTableState(self):
        n = datetime.datetime.utcnow()
        now = make_aware(n)

        if now < self.db.updateTimer + datetime.timedelta(milliseconds=333):
            return

        self.lockForUpdate()

        r = True
        while r:
            if self.db.state == TableStates.RESET:
                r = self.stateReset()
                continue
            if self.db.state == TableStates.NOGAME:
                r = self.stateNoGame()
                continue
            if self.db.state == TableStates.SETUP:
                r = self.stateSetup()
                continue
            if self.db.state == TableStates.SETUP_BUTTON:
                r = self.stateSetupButton()
                continue
            if self.db.state == TableStates.SETUP_DEAL:
                r = self.stateSetupDeal()
                continue
            if self.db.state == TableStates.SETUP_SMALL_BLIND:
                r = self.stateSetupSmallBlind()
                continue
            if self.db.state == TableStates.SETUP_BIG_BLIND:
                r = self.stateSetupBigBlind()
                continue
            # if self.db.state == TableStates.ROUNDS:
            #     r = self.stateRounds()
            #     continue
            # if self.db.state == TableStates.ROUNDS_DEAL:
            #     r = self.stateRoundsDeal()
            #     continue
            if self.db.state == TableStates.ROUNDS_BETTING:
                r = self.stateRoundsBetting()
                continue
            # if self.db.state == TableStates.ROUNDS_LAST_MAN_STANDING:
            #     r = self.stateRoundsLastManStanding()
            #     continue
            # if self.db.state == TableStates.SHOWDOWN:
            #     r = self.stateShowdown()
            #     continue

            r = False   # No hit? then exit the loop

        self.db.updateTimer = now
        self.save()


    # def updateWithoutAction(self):
    #     # If game is not active then try to start it
    #     if self.getState() == 0:
    #         nrActive = 0
    #         for i in self.getPlayerRange():
    #             if self.isPlayerReadyToEnter(i):
    #                 nrActive += 1
    #
    #         if nrActive >= 2:
    #             self.setState(1)
    #             self.setBoardCards('')
    #             self.setPot(0)
    #             self.setDealer(self.nextPlayerReadyToEnter(self.getDealer()))
    #             self.createDeck()
    #
    #             # Deal cards
    #             for i in self.getPlayerRange():
    #                 if self.isPlayerReadyToEnter(i):
    #                     card1 = self.drawCardFromDeck()
    #                     card2 = self.drawCardFromDeck()
    #                     self.setPlayerCards(i, card1+card2)
    #                     self.setPlayerBet(i, 0)
    #
    #             sb_pos = self.nextPlayerReadyToEnter(self.getDealer())
    #             self.setPlayerBet(sb_pos, self.getBlind()/2)
    #             self.setPlayerMoney(sb_pos, self.getPlayerMoney(sb_pos)-self.getPlayerBet(sb_pos))
    #
    #             bb_pos = self.nextPlayerReadyToEnter(sb_pos)
    #             self.setPlayerBet(bb_pos, self.getBlind())
    #             self.setPlayerMoney(bb_pos, self.getPlayerMoney(bb_pos)-self.getPlayerBet(bb_pos))
    #
    #             self.setNextToAct(self.getNextPlayerStillInTheGame(bb_pos))
    #             self.setLastToAct(self.getPreviousPlayerStillInTheGame(self.getNextToAct()))
    #
    #             self.db.save()
    #
    #     # If game is active then update on timers etc.
    #     if self.getState() == 1:
    #         # If there is only one player left then they win the pot
    #         winner = None
    #         if self.getNrOfPlayersWithCards() == 1:
    #             winnings = self.getPot()
    #             for i in self.getPlayerRange():
    #                 if self.getPlayerCards(i):
    #                     winner = i
    #                 winnings += self.getPlayerBet(i)
    #                 self.setPlayerBet(i, 0)
    #
    #             self.setPlayerMoney(winner, self.getPlayerMoney(winner) + winnings)
    #
    #             self.setState(0)
    #             self.setPot(0)
    #             self.setBoardCards('')
    #             self.db.save()
    #
    #     if self.getState() == 2:
    #         release = self.getShowDownTimer() + datetime.timedelta(seconds=5)
    #         if make_aware(datetime.datetime.utcnow()) < release:
    #             print('Time not expired', datetime.datetime.utcnow(), release)
    #             return
    #
    #         print('Time expired', datetime.datetime.utcnow(), release)
    #         winner = None
    #         highest = 0
    #         for i in self.getPlayerRange():
    #             c = self.getPlayerCards(i)
    #             b = self.getBoardCards()
    #             if c:
    #                 hole = [pokerFunctions.cardTranslate(c[0:2]),
    #                         pokerFunctions.cardTranslate(c[2:4])]
    #                 board = [pokerFunctions.cardTranslate(b[0:2]),
    #                          pokerFunctions.cardTranslate(b[2:4]),
    #                          pokerFunctions.cardTranslate(b[4:6]),
    #                          pokerFunctions.cardTranslate(b[6:8]),
    #                          pokerFunctions.cardTranslate(b[8:10])]
    #                 score = HandEvaluator.evaluate_hand(hole, board)
    #                 if score > highest:
    #                     highest = score
    #                     winner = i
    #         print(winner, score)
    #
    #         winnings = self.getPot()
    #         for i in self.getPlayerRange():
    #             winnings += self.getPlayerBet(i)
    #             self.setPlayerBet(i, 0)
    #
    #         self.setPlayerMoney(winner, self.getPlayerMoney(winner) + winnings)
    #
    #         self.setState(0)
    #         self.setPot(0)
    #         self.setBoardCards('')
    #         self.db.save()
    #
    #
    #
    # def updateOnAction(self):
    #     # If state is zero then game is not active
    #     if self.getState() == 0:
    #         return
    #
    #     # If this player raised we need to update last-to-act
    #     if self.didNextToActRaise():
    #         self.setLastToAct(self.getPreviousPlayerStillInTheGame(self.getNextToAct()))
    #
    #     # If player was the last to act then go to next round
    #     if self.getNextToAct() == self.getLastToAct():
    #         if len(self.getBoardCards()) < 10:
    #             bets = 0
    #             for i in self.getPlayerRange():
    #                 bets += self.getPlayerBet(i)
    #                 self.setPlayerBet(i, 0)
    #             bets += self.getPot()
    #             self.setPot(bets)
    #
    #             newCard = self.drawCardFromDeck()
    #
    #             self.setBoardCards(self.getBoardCards() + newCard)
    #
    #             self.setNextToAct(self.getNextPlayerStillInTheGame(self.getDealer()))
    #             self.setLastToAct(self.getPreviousPlayerStillInTheGame(self.getNextToAct()))
    #         else:
    #             # Showdown
    #             self.setState(2)
    #             self.setShowDownCounter()
    #             self.save()
    #
    #     else:   # Or go to the next player
    #         print('3')
    #         self.setNextToAct(self.getNextPlayerStillInTheGame(self.getNextToAct()))
    #
    #     self.db.save()