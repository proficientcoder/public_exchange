import random
import pytz
import time
import datetime
from django.conf import settings
from django.utils.timezone import make_aware
from user.models import apiKey
from django.contrib.auth.models import User
from django.db import transaction

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
    ROUNDS_PREBETTING = 20000
    ROUNDS_DEAL = 21000
    ROUNDS_BETTING = 22000
    ROUNDS_LAST_MAN_STANDING = 23000
    SHOWDOWN = 30000


class PokerTable:
    db = None
    username = None

    def __init__(self, request, id):
        tmp = pokerModels.PokerTable.objects.filter(id=id)
        if len(tmp) != 1:
            raise LookupError   # The table id could not be found

        self.db = tmp[0]

        if 'key' in request.GET:
            self.username = userFunctions.getUserFromKey(request)

    def lockForUpdate(self):
        with transaction.atomic():
            tmp = pokerModels.PokerTable.objects.select_for_update(nowait=True).filter(id=self.db.pk)
            if len(tmp) != 1:
                raise LookupError   # The table id could not be found

        self.db = tmp[0]

    def save(self):
        self.db.save()

    def delete(self):
        self.db.delete()

    def getSize(self):
        return int(self.db.size)

    def getPlayerName(self, nr):
        return getattr(self.db, f'player_{nr}')

    def setPlayerCards(self, nr, what):
        setattr(self.db, f'player_{nr}_cards', what)

    def getPlayerCards(self, nr):
        return getattr(self.db, f'player_{nr}_cards')

    def setPlayerNewBet(self, nr, what):
        setattr(self.db, f'player_{nr}_new_bet', what)

    def getPlayerNewBet(self, nr):
        return int(getattr(self.db, f'player_{nr}_new_bet'))

    def setPlayerPrevBet(self, nr, what):
        setattr(self.db, f'player_{nr}_prev_bet', what)

    def getPlayerPrevBet(self, nr):
        return int(getattr(self.db, f'player_{nr}_prev_bet'))

    def setPlayerMoney(self, nr, what):
        setattr(self.db, f'player_{nr}_money', what)

    def getPlayerMoney(self, nr):
        return int(getattr(self.db, f'player_{nr}_money'))

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
        return int(self.db.pot)

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
        return int(self.db.blind)

    def getPlayer(self, nr):
        return getattr(self.db, f'player_{nr}')

    def setPlayer(self, nr, what):
        setattr(self.db, f'player_{nr}', what)

    def getPlayerAction(self, nr):
        return getattr(self.db, f'player_{nr}_action')

    def setPlayerAction(self, nr, what):
        setattr(self.db, f'player_{nr}_action', what)

    def getPlayerLeave(self, nr):
        return getattr(self.db, f'player_{nr}_leave')

    def setPlayerLeave(self, nr, what):
        setattr(self.db, f'player_{nr}_leave', what)

    def getPlayerJoin(self, nr):
        return getattr(self.db, f'player_{nr}_join')

    def setPlayerJoin(self, nr, what):
        setattr(self.db, f'player_{nr}_join', what)

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
        return self.getPlayerName(self.getNextToAct()) == self.username

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

    def concatBets(self):
        for i in self.getPlayerRange():
            self.setPlayerPrevBet(i, self.getPlayerPrevBet(i) + self.getPlayerNewBet(i))
            self.setPlayerNewBet(i, 0)

    def addLog(self, txt):
        log = self.db.log
        if not log:
            log = ''

        log = log.split('|')
        log.append(txt)
        while len(log) > 25:
            log.pop(0)
        self.db.log = '|'.join(log)

    def getLog(self):
        log = self.db.log
        if not log:
            return []

        log = log.split('|')
        return log

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
            'log': self.getLog(),
            'you': None,
        }

        if self.user != None:
            state['you'] = self.username

        if self.db.eventTimer:
            n = datetime.datetime.utcnow()
            now = make_aware(n)
            time_left = (self.db.eventTimer - now).total_seconds()
            state['timer'] = time_left

        max_bet = 0
        for i in self.getPlayerRange():
            max_bet = max(max_bet, self.getPlayerNewBet(i))

        for i in self.getPlayerRange():
            if self.isPlayer(i):
                state['players'].append({'id': i,
                                         'name': self.getPlayer(i),
                                         'balance': self.getPlayerMoney(i),
                                         'new_bet': self.getPlayerNewBet(i),
                                         'prev_bet': self.getPlayerPrevBet(i),
                                         'cards': self.getPlayerCards(i),
                                         })
                if self.user != None:
                    if self.getPlayer(i) != self.user and self.getState() != TableStates.SHOWDOWN:
                        if state['players'][-1]['cards']:
                            state['players'][-1]['cards'] = ''

                    if i == self.getNextToAct() and self.getPlayer(i) == self.user and self.getState() == TableStates.ROUNDS_BETTING:
                        actor_bet = self.getPlayerNewBet(self.getNextToAct())

                        if max_bet == actor_bet:
                            state['actions'].append('CHECK')

                        if max_bet > actor_bet:
                            state['actions'].append('FOLD')
                            state['actions'].append('CALL')

                        if max_bet == 0:
                            state['actions'].append('BET')
                        else:
                            state['actions'].append('RAISE')

            else:
                state['players'].append(None)

        return state


    def stateReset(self):
        #self.db.state = -1
        #self.db.dealer = 0
        #self.db.next_to_act = 0
        #self.db.last_to_act = 0
        #self.db.blind = 10
        self.db.deck = None
        self.db.board = None
        self.db.eventTimer = None
        self.db.updateTimer = None

        self.db.player_0_cards = None
        self.db.player_0_new_bet = 0
        self.db.player_0_prev_bet = 0
        #self.db.player_0_money = 50
        self.db.player_0_action = False

        self.db.player_1_cards = None
        self.db.player_1_new_bet = 0
        self.db.player_1_prev_bet = 0
        #self.db.player_1_money = 50
        self.db.player_1_action = False

        self.db.player_2_cards = None
        self.db.player_2_new_bet = 0
        self.db.player_2_prev_bet = 0
        #self.db.player_2_money = 50
        self.db.player_2_action = False

        self.db.state = TableStates.NOGAME

        return True


    def stateNoGame(self):
        # Kick out people with leave flag
        for i in self.getPlayerRange():
            if self.getPlayerLeave(i):
                log = self.getPlayerName(i) + ' left the table'
                self.addLog(log)
                self.setPlayer(i, None)
                # TODO Move money
                self.setPlayerLeave(i, False)

        # Kick out poor people
        for i in self.getPlayerRange():
            if self.getPlayerMoney(i) == 0 and self.getPlayer(i):
                log = self.getPlayerName(i) + ' got kicked from the table'
                self.addLog(log)
                self.setPlayer(i, None)

        # Enough players to start a game?
        nrActive = 0
        for i in self.getPlayerRange():
            if self.isPlayerReadyToEnter(i):
                nrActive += 1

        if nrActive >= 2:
            self.setState(TableStates.SETUP)

        return False

    def stateSetup(self):
        self.createDeck()
        self.setState(TableStates.SETUP_DEAL)

        return True

    def stateSetupDeal(self):
        # Deal cards
        self.addLog('')
        self.addLog('Starting new round')
        for i in self.getPlayerRange():
            if self.isPlayerReadyToEnter(i):
                u = self.getPlayerName(i) + ' has ' + str(self.getPlayerMoney(i))
                self.addLog(u)
                card1 = self.drawCardFromDeck()
                card2 = self.drawCardFromDeck()
                self.setPlayerCards(i, card1 + card2)

        self.setState(TableStates.SETUP_BUTTON)

        return True

    def stateSetupButton(self):
        dealer_pos = self.findNextPlayerToAct(self.getDealer())
        self.setDealer(dealer_pos)
        self.setNextToAct(self.findNextPlayerToAct(dealer_pos))
        u = self.getPlayerName(dealer_pos) + ' has the button'
        self.addLog(u)

        self.setState(TableStates.SETUP_SMALL_BLIND)
        return True

    def stateSetupSmallBlind(self):
        sb_pos = self.getNextToAct()
        amount = int(self.getBlind() / 2)
        self.setPlayerNewBet(sb_pos, amount)
        self.setPlayerMoney(sb_pos, self.getPlayerMoney(sb_pos) - amount)
        self.setNextToAct(self.findNextPlayerToAct(self.getNextToAct()))

        u = self.getPlayerName(sb_pos) + ' posts the small blind of ' + str(amount)
        self.addLog(u)

        self.setState(TableStates.SETUP_BIG_BLIND)
        return True

    def stateSetupBigBlind(self):
        bb_pos = self.getNextToAct()
        amount = self.getBlind()
        self.setPlayerNewBet(bb_pos, amount)
        self.setPlayerMoney(bb_pos, self.getPlayerMoney(bb_pos) - amount)
        self.setNextToAct(self.findNextPlayerToAct(self.getNextToAct()))
        self.setLastToAct(self.findPrevPlayerToAct(self.getNextToAct()))

        u = self.getPlayerName(bb_pos) + ' posts the big blind of ' + str(amount)
        self.addLog(u)

        # Who wants to join?
        for i in self.getPlayerRange():
            if self.getPlayerJoin(i):
                self.setPlayerJoin(i, False)
                u = self.getPlayerName(bb_pos) + ' joined the table'
                self.addLog(u)
                # difference = self.getBlind() - self.getPlayerNewBet(i)
                # if difference > 0:
                #     self.setPlayerNewBet(bb_pos, amount)
                #     self.setPlayerMoney(bb_pos, self.getPlayerMoney(bb_pos) - difference)
                #     u = self.getPlayerName(i) + ' joining the table adds' + str(amount)
                #     self.addLog(u)

        self.setState(TableStates.ROUNDS_BETTING)   # Go straight into the betting part
        return True

    def stateRoundsPreBetting(self):
        howManyCanAct = 0
        for i in self.getPlayerRange():
            if self.isPlayerAbleToAct(i):
                howManyCanAct += 1

        if howManyCanAct < 2:
            if self.getBoardCards():
                if len(self.getBoardCards()) == 10:
                    self.concatBets()
                    self.db.eventTimer = None
                    self.setState(TableStates.SHOWDOWN)
                    return True

            self.concatBets()
            self.setState(TableStates.ROUNDS_DEAL)
            return True

        self.setState(TableStates.ROUNDS_BETTING)
        return True


    def stateRoundsBetting(self):
        # Last man standing
        howManyInGame = 0
        for i in self.getPlayerRange():
            if self.isPlayerInGame(i):
                howManyInGame += 1

        if howManyInGame < 2:
            self.concatBets()
            self.db.eventTimer = None
            self.setState(TableStates.ROUNDS_LAST_MAN_STANDING)
            return True

        # Did player act
        didAct = self.getPlayerAction(self.getNextToAct())
        if didAct:
            self.setPlayerAction(self.getNextToAct(), False)
            self.db.eventTimer = None

            if self.getNextToAct() == self.getLastToAct():
                if self.getBoardCards():
                    if len(self.getBoardCards()) == 10:
                        self.concatBets()
                        self.db.eventTimer = None
                        self.setState(TableStates.SHOWDOWN)
                        return True

                self.concatBets()
                self.setState(TableStates.ROUNDS_DEAL)
                return True

            # Next player
            self.setNextToAct(self.findNextPlayerToAct(self.getNextToAct()))

        # Did time run out
        n = datetime.datetime.utcnow()
        now = make_aware(n)
        if self.db.eventTimer is None:
            self.db.eventTimer = now + datetime.timedelta(seconds=30)

        if now < self.db.eventTimer:
            return False

        log = self.getPlayerName(self.getNextToAct()) + ' timed out'
        self.addLog(log)

        log = self.getPlayerName(self.getNextToAct()) + ' folded'
        self.addLog(log)

        self.setPlayerCards(self.getNextToAct(), None)
        self.db.eventTimer = None
        self.setNextToAct(self.findNextPlayerToAct(self.getNextToAct()))

        return True

    def stateRoundsDeal(self):
        bc = self.getBoardCards()

        amount = 1
        if not bc:
            bc = ''
            amount = 3

        log = ''
        if len(bc) == 0:
            log = 'Flop '
        if len(bc) == 6:
            log = 'Turn '
        if len(bc) == 8:
            log = 'River '

        for i in range(0, amount):
            card = self.drawCardFromDeck()
            bc += card
            log += card + ' '
            self.setBoardCards(bc)

        self.addLog(log)

        self.setNextToAct(self.findNextPlayerToAct(self.getDealer()))
        self.setLastToAct(self.findPrevPlayerToAct(self.getNextToAct()))
        self.setState(TableStates.ROUNDS_PREBETTING)
        return True

    def stateShowdown(self):
        n = datetime.datetime.utcnow()
        now = make_aware(n)

        if self.db.eventTimer is None:
            self.db.eventTimer = now + datetime.timedelta(seconds=3)
            return False

        if now < self.db.eventTimer:
            return False

        scores = []
        bets = []
        winnings = []
        for i in self.getPlayerRange():
            winnings.append(0)
            if self.getPlayerCards(i):
                log = self.getPlayerName(i) + ' shows ' + self.getPlayerCards(i)
                self.addLog(log)

                c = self.getPlayerCards(i)
                b = self.getBoardCards()
                if c:
                    hole = [pokerFunctions.cardTranslate(c[0:2]),
                            pokerFunctions.cardTranslate(c[2:4])]
                    board = [pokerFunctions.cardTranslate(b[0:2]),
                             pokerFunctions.cardTranslate(b[2:4]),
                             pokerFunctions.cardTranslate(b[4:6]),
                             pokerFunctions.cardTranslate(b[6:8]),
                             pokerFunctions.cardTranslate(b[8:10])]
                    score = HandEvaluator.evaluate_hand(hole, board)
                    scores.append(score)
                    bets.append(self.getPlayerPrevBet(i))
            else:
                scores.append(0)
                bets.append(0)

        while sum(scores) > 0:
            best = min([i for i in scores if i != 0])
            count = scores.count(best)
            winner = scores.index(best)

            for i in self.getPlayerRange():
                part = int(bets[i] / count)
                collect = min(part, bets[i])
                winnings[winner] += collect
                bets[i] -= collect

            scores[winner] = 0

        for i in self.getPlayerRange():
            self.setPlayerMoney(i, self.getPlayerMoney(i) + winnings[i])
            if winnings[i] != 0:
                log = self.getPlayerName(i) + ' won ' + str(winnings[i])
                self.addLog(log)

        self.db.eventTimer = None
        self.setState(TableStates.RESET)
        return True

    def stateRoundsLastManStanding(self):
        n = datetime.datetime.utcnow()
        now = make_aware(n)

        if self.db.eventTimer is None:
            self.db.eventTimer = now + datetime.timedelta(seconds=3)
            return False

        if now < self.db.eventTimer:
            return False

        winner = None
        winnings = 0
        for i in self.getPlayerRange():
            if self.getPlayerCards(i) is not None:
                winner = i
            winnings += self.getPlayerPrevBet(i)
            winnings += self.getPlayerNewBet(i)

        self.setPlayerMoney(winner, self.getPlayerMoney(winner) + winnings)

        log = self.getPlayerName(winner) + ' won ' + str(winnings)
        self.addLog(log)

        self.db.eventTimer = None
        self.setState(TableStates.RESET)
        return True


    def updateTableState(self):
        n = datetime.datetime.utcnow()
        now = make_aware(n)

        if self.db.updateTimer == None:    # Brand new table
            self.lockForUpdate()
            self.db.updateTimer = now
            self.save()

        if now < self.db.updateTimer:
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
            if self.db.state == TableStates.ROUNDS_PREBETTING:
                r = self.stateRoundsPreBetting()
                continue
            if self.db.state == TableStates.ROUNDS_DEAL:
                r = self.stateRoundsDeal()
                continue
            if self.db.state == TableStates.ROUNDS_BETTING:
                r = self.stateRoundsBetting()
                continue
            if self.db.state == TableStates.ROUNDS_LAST_MAN_STANDING:
                r = self.stateRoundsLastManStanding()
                continue
            if self.db.state == TableStates.SHOWDOWN:
                r = self.stateShowdown()
                continue

            r = False   # No hit? then exit the loop

        self.db.updateTimer = now + datetime.timedelta(milliseconds=333)
        self.save()

