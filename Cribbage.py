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
    # ----- Class Variables ----- #
    SUIT = {"Clubs", "Diamonds", "Hearts", "Spades"}
    RANK = {"Ace", 2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King"}

    # ----- Functions ----- #
    # Makes the deck 52 cards (we will remove them randomly bc currDeck is a set, so we don't need to actually shuffle)
    def shuffle(self):
        self.currDeck = set(product(self.__class__.RANK, self.__class__.SUIT)) # taking the cartesian product

     # Returns n randomly chosen cards, and removes them from the deck
    def draw(self, n):
        cardTuple = [self.currDeck.pop() for i in range(n)] # returns a list of cards in the form (RANK, SUIT)
        cards = []
        for i in range(n):
            cards.append(str(cardTuple[i][0]) + ' of ' + str(cardTuple[i][1]))
        return cards

class Player:
    '''Implements a player of a cribbage game'''
    # ----- Constructor ----- #
    def __init__(self, n):
        self.PLAYER_NUMBER = n
        self.handInvisible = []
        self.handVisible = []
        self.points = 0 
        self.counted = False # whether or not the player's hand has been counted yet

    # ----- Functions ----- # 
    # Draws a hand of 6 (given) cards
    # # Actually, tracks two hands:
        # handInvisible, which contains all cards only this player can see
        # handVisible, which contains all cards other players can see (is initiated to as an empty list)
    def drawHand(self, card1, card2, card3, card4, card5, card6):
        self.handInvisible = [card1, card2, card3, card4, card5, card6]
        self.handVisible = []
        self.counted = False

    # Makes their whole hand visible
    def playHand(self):
        self.handVisible = self.handVisible + self.handInvisible
        self.handInvisible = []

    # Adds n points to their total
    def addPoints(self, n):
        self.points += n
        self.counted = True

class CurrPlayer(Player):
    '''Implements all of the knowledge and actions of a user (of a player)'''
    # ----- Class Variables ----- #
    NUM_PLAYERS = 0
    PLAYERS = [] # a list of all the players in the game

    # ----- Constructor ----- #
    # Takes in the assigned number for this player
    def __init__(self, n):
        super().__init__(n)
        # initializing list of players
        #self.__class__.PLAYERS = [OtherPlayer(i+1) for i in range(n-1)] 
        self.__class__.PLAYERS.append("Empty") # so that players start indexing at 1
        for i in range(n-1):
            self.addPlayer()
        self.__class__.PLAYERS.append(self)
        self.NUM_PLAYERS += 1

    # ----- Functions ----- #
    def addPlayer(self):
        self.NUM_PLAYERS += 1
        self.__class__.PLAYERS.append(OtherPlayer(self.NUM_PLAYERS))

class OtherPlayer(Player):
    '''Implements all of the information about other players from the perspective of the user'''

    def __init__(self, n):
        super().__init__(n)

# ----- Test Cases ----- #
if __name__ == '__main__':
    ### Testing module #####
        # drawing hands for all players
        
    ### Testing Deck #####
        deck = Deck()
        deck.shuffle()
        #print("A fresh standard deck is:", deck.currDeck)
        print("A randomly drawn card is:", deck.draw(1))
        print("A randomly drawn hand is:", deck.draw(6))
        #print("The number of remaining cards is: 45 ==", len(deck.currDeck), "?")

    ### Testing Player #####
        #alice = Player(4)
        #print("Alice's player numebr is", alice.PLAYER_NUMBER)
        # drawHand()
        #    print("ACTION: Alice draws a hand")
        #    alice.drawHand("Ace", 5, 3, "Jack", 10, "King")
        #    print("Alice's hidden hand:", alice.handInvisible)
        #    print("Alice's visible hand:", alice.handVisible)
        # playHand()
        #    print("ACTION: Alice plays her hand")
        #    alice.playHand()
        #    print("Alice's hidden hand:", alice.handInvisible)
        #    print("Alice's visible hand:", alice.handVisible)

    ### Testing CurrPlayer #####
        me = CurrPlayer(4)
        print("My player number is", me.PLAYER_NUMBER)
        print("The players numbers are", [me.PLAYERS[i].PLAYER_NUMBER for i in range(1,me.NUM_PLAYERS+1)])
        print([i+1 for i in range(me.NUM_PLAYERS)])
    ### Testing OtherPlayer #####
        #otherPlayer = OtherPlayer(3)
        #print("otherPlayer's number is ", otherPlayer.PLAYER_NUMBER)