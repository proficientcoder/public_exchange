import random
from user.models import apiKey
from django.contrib.auth.models import User

import poker.models as pokerModels
import user.functions as userFunctions


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

    def setPlayerBet(self, nr, what):
        setattr(self.db, f'player_{nr}_bet', what)

    def getPlayerBet(self, nr):
        return float(getattr(self.db, f'player_{nr}_bet'))

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
        return range(1, self.db.size + 1)

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

    def setPot(self, what):
        self.db.pot = what

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

    def getNextPlayerStillInTheGame(self, position):
        position += 1
        if position > self.db.size:
            position = 1
        while getattr(self.db, f'player_{position}') is None:
            position += 1
            if position > self.db.size:
                position = 1

        return position

    def getPreviousPlayerStillInTheGame(self, position):
        position -= 1
        if position < 1:
            position = self.db.size
        while getattr(self.db, f'player_{position}') is None:
            position -= 1
            if position < 1:
                position = self.db.size

        return position

    # The big stuff

    def updateWithoutAction(self):
        # If game is not active then try to start it
        if self.getState() == 0:
            nrActive = 0
            for i in self.getPlayerRange():
                if self.isPlayerReadyToEnter(i):
                    nrActive += 1

            if nrActive >= 2:
                self.setState(1)
                self.setBoardCards('')
                self.setPot(0)
                self.setDealer(self.nextPlayerReadyToEnter(self.getDealer()))
                self.createDeck()

                # Deal cards
                for i in self.getPlayerRange():
                    if self.isPlayerReadyToEnter(i):
                        card1 = self.drawCardFromDeck()
                        card2 = self.drawCardFromDeck()
                        self.setPlayerCards(i, card1+card2)
                        self.setPlayerBet(i, 0)

                sb_pos = self.nextPlayerReadyToEnter(self.getDealer())
                self.setPlayerBet(sb_pos, self.getBlind()/2)
                self.setPlayerMoney(sb_pos, self.getPlayerMoney(sb_pos)-self.getPlayerBet(sb_pos))

                bb_pos = self.nextPlayerReadyToEnter(sb_pos)
                self.setPlayerBet(bb_pos, self.getBlind())
                self.setPlayerMoney(bb_pos, self.getPlayerMoney(bb_pos)-self.getPlayerBet(bb_pos))

                self.setNextToAct(self.getNextPlayerStillInTheGame(bb_pos))
                self.setLastToAct(self.getPreviousPlayerStillInTheGame(self.getNextToAct()))

                self.db.save()

        # If game is active then update on timers etc.
        if self.getState() == 1:
            pass


    def updateOnAction(self):
        # If state is zero then game is not active
        if self.getState() == 0:
            self.db.save()

        # If there is only one player left then they win the pot
        winner = None
        if self.getNrOfPlayersWithCards() == 1:
            winnings = self.getPot()
            for i in self.getPlayerRange():
                if self.getPlayerCards(i):
                    winner = i
                winnings += self.getPlayerBet(i)
                self.setPlayerBet(i, 0)

            self.setPlayerMoney(winner, self.getPlayerMoney(winner) + winnings)

            self.setState(0)
            self.setPot(0)
        else:
            # If this player raised we need to update last-to-act
            if self.didNextToActRaise():
                print('1')
                self.setLastToAct(self.getPreviousPlayerStillInTheGame(self.getNextToAct()))

            # If player was the last to act then go to next round
            if self.getNextToAct() == self.getLastToAct():
                print('2')
                if len(self.getBoardCards()) < 10:
                    bets = 0
                    for i in self.getPlayerRange():
                        bets += self.getPlayerBet(i)
                        self.setPlayerBet(i, 0)
                    bets += self.getPot()
                    self.setPot(bets)

                    newCard = self.drawCardFromDeck()

                    self.setBoardCards(self.getBoardCards() + newCard)

                    self.setNextToAct(self.getNextPlayerStillInTheGame(self.getDealer()))
                    self.setLastToAct(self.getPreviousPlayerStillInTheGame(self.getNextToAct()))

            else:   # Or go to the next player
                print('3')
                self.setNextToAct(self.getNextPlayerStillInTheGame(self.getNextToAct()))

        self.db.save()