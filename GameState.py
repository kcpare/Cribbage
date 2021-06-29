# Kathryn Pare
# Cribbage Game State

# GameState tracks the state of the game (stage, players involved, deck, the status of all hands with regard to being drawn, counted, etc)

import enum
from Cribbage import Player

class GameState:
    '''A class to store info about the state of the game'''
    # ----- Class Variables ----- #
    MAX_PLAYERS = 4

    def __init__(self):
        self.CURR_STAGE = STAGES(1) # Possible stages: ("START", "DRAW", "PLAY", "COUNT")

        self.PLAYERS = ["Empty"] # a list of Player Objects, also indexed starting at 1

        self.deck = Deck() # the deck we'll be playing with
        self.deck.shuffle() # creating (and shuffling) a deck 

        self.handsDrawn = 0 # number of hands drawn
        self.handsCounted = 0 # number of hands counted

    # ----- Methods ----- #
    def moveToNextStage(self):
        self.CURR_STAGE = self.CURR_STAGE.nextStage()

    def addPlayer(self, newPlayer):
        self.PLAYERS.append(newPlayer)
    
    def removePlayer(self, playerNumber):
        del self.PLAYERS[[playerNumber]]

    # Draws a hand from a deck, assigns to the given player, and marks one more hand as drawn
    def drawPlayerHand(self, playerNumber):
        hand = self.deck.draw(6)
        self.PLAYERS[playerNumber].drawHand(hand[0], hand[1], hand[2], hand[3], hand[4], hand[5])
        self.handsDrawn += 1

    # Returns whether all player hands have been dealt
    def areAllHandsDealt(self):
        return if self.handsDrawn == (len(self.PLAYERS)-1) # we have an extra "empty" player in order to start indexing at 1

    # Plays the player's hands and returns it
    def playPlayerHand(self, playerNumber):
        self.PLAYERS[playerNumber].playHand()
        return self.PLAYERS[playerNumber].handVisible
    
    # returns whether or not the player with the given playerNumber has played their hand
    def hasPlayedHand(self, playerNumber):
        return len(self.PLAYERS[playerNumber].handVisible) == 6

    # returns whether or not the player with the given playerNumber has counted their hand
    def hasCountedHand(self, playerNumber):
        self.PLAYERS[playerNumber].counted == False

    # Gives the player with the given playerNumber the given number of points
    # Marks that player has having their hand counted
    def addPointsToPlayer(self, playerNumber, points):
        self.PLAYERS[playerNumber].addPoints(points)
        self.handsCounted += 1

    # Returns whether or not all hands have been counted
    def areAllHandsCounted(self):
        return self.handsCounted == (len(self.PLAYERS)-1) # we have an extra "empty" player in order to start indexing at 1

    # Resets the board (resets handsDrawn, handsCounted, and shuffles the deck)
    def resetBoard(self):
        self.handsCounted = 0
        self.handsDrawn = 0
        self.deck.shuffle()

    # ----- Get Methods ----- #
    def getCurrStage(self):
        return self.CURR_STAGE

    def getPlayer(self, playerNumber):
        return self.PLAYERS[playerNumber]

    def getNumberOfPlayers(self):
        return len(self.PLAYERS) - 1 # we have an extra "empty" player in order to start indexing at 1

    # ----- Helper Methods ----- #
    def resetHandsDrawn(self):
        self.handsDrawn = 0

    def resetHandsCounted(self):
        self.handsCounted = 0

# An enumerated type which describes the possible stages of this Cribbage game
class STAGES(enum.Enum):
    START = 1
    DRAW = 2
    PLAY = 3
    COUNT = 4
    END = 5

    # A method to grab the next stage, wrapping back to START when END is reached
    def nextStage(self):
        nextVal = self.value + 1
        if nextVal < END.value:
            return STAGES(nextVal)
        else:
            return STAGES(1)