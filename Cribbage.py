# Kathryn Pare
# Cribbage Module

##### Description #####
# This module defines a set of classes that describe a game of Cribbage  
# 
# Some points of note:
#   Decks are implemented as sets
#   Player hands are implemented as lists
#   Individual cards are implemented as tuples (RANK, SUIT)
#
#   Players are numbered starting at 1

from itertools import product # cartesian product operation

class Deck:
    '''Implements a standard deck of 52 cards'''
    # ---------------------------------------- Class Variables ---------------------------------------- #
    SUIT = {"Clubs", "Diamonds", "Hearts", "Spades"}
    RANK = {"Ace", 2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King"}

    # -------------------- Functions -------------------- #
    def shuffle(self):
        '''Creates a 52 card deck (Please note we remove cards randomly, so it is not actually shuffled).'''
        self.currDeck = set(product(self.__class__.RANK, self.__class__.SUIT)) # taking the cartesian product

    def draw(self, n):
        '''Returns n randomly chosen cards, and removes them from the deck'''
        cardTuple = [self.currDeck.pop() for i in range(n)] # returns a list of cards in the form (RANK, SUIT)
        cards = []
        for i in range(n):
            cards.append(str(cardTuple[i][0]) + ' of ' + str(cardTuple[i][1]))
        return cards

class Player:
    '''Implements a player of a cribbage game'''
    # -------------------- Constructor -------------------- #
    def __init__(self, n):
        self.PLAYER_NUMBER = n
        self.handInvisible = []
        self.handVisible = []
        self.points = 0 
        self.counted = False # whether or not the player's hand has been counted yet

    # -------------------- Functions -------------------- # 
    def drawHand(self, card1, card2, card3, card4, card5, card6):
        '''Draws a hand of 6 (given) cards. Actually, two hands are tracked: handInvisible, which contains all cards only this player can see, and handVisible, 
        which contains all cards other players can see (is initiated as an empty list).'''
        self.handInvisible = [card1, card2, card3, card4, card5, card6]
        self.handVisible = []
        self.counted = False

    def playHand(self):
        '''Makes this player's hand completely visible.'''
        self.handVisible = self.handVisible + self.handInvisible
        self.handInvisible = []

    def addPoints(self, n):
        '''Adds n points to this player's total points.'''
        self.points += n
        self.counted = True

class CurrPlayer(Player):
    '''Implements all of the knowledge and actions of a user (of a player)'''
    # -------------------- Class Variables -------------------- #
    NUM_PLAYERS = 0
    PLAYERS = [] # a list of all the players in the game

    # -------------------- Constructor -------------------- #
    # Takes in the assigned number for this player
    def __init__(self, n):
        super().__init__(n)
        # initializing list of players
        #self.__class__.PLAYERS = [Player(i+1) for i in range(n-1)] 
        self.__class__.PLAYERS.append("Empty") # so that players start indexing at 1
        for i in range(n-1):
            self.addPlayer()
        self.__class__.PLAYERS.append(self)
        self.NUM_PLAYERS += 1

    # -------------------- Functions -------------------- #
    def addPlayer(self):
        '''Notifies this player about a new opponent so that it can be tracked with their PLAYERS list.'''
        self.NUM_PLAYERS += 1
        self.__class__.PLAYERS.append(Player(self.NUM_PLAYERS))
