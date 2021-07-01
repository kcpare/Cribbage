# Kathryn Pare
# Cribbage Game State

from ..Action import Action
from GameState import GameState
from GameState import STAGES

# StartGame implements Action to define how a player can play their hand
class PlayPlayerHand(Action):
    COMMAND = "!play"

    def __init__(self, gameState):
        self.GAMESTATE = gameState

    # The command associated with their action (ex. !draw, !play, !count). By convention, these are prefaced with an exclaimation mark
    def getActionCommand(self):
        return self.__class__.COMMAND

    # An algorithm to validate execute the action along with any player input following the action, which takes in the player number
    # - This returns the server's 'response' back, which is a list of either:
    # -- length 1 for a (string) message back to that player, or
    # -- length 2 for a (string) message back to that player and a (string) message for all other players
    def execute(self, playerNumber, input):
        response = []
        if self.GAMESTATE.getCurrStage() == STAGES.PLAY:
            if self.GAMESTATE.getPlayer(playerNumber).handInvisible: # if their hand has not already been played (is not empty)
                hand = self.GAMESTATE.playPlayerHand(playerNumber)
                response.append("You played you hand: " + str(hand))
                response.append("Player" + str(playerNumber) + " has played: " + str(hand))

                # testing whehter we need to switch to next stage
                if self.GAMESTATE.areAllHandsPlayed():
                    self.GAMESTATE.moveToNextStage()
            else: # if their hand has already been played
                response.append("Sorry, you already played your hand!")
        else:
            response.append("Sorry, we're not playing hands right now!")
        return response
