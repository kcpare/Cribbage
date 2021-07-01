# Kathryn Pare
# Cribbage Game State

from ..Action import Action
from GameState import GameState
from GameState import STAGES

# StartGame implements Action to define how a player can draw their hand
class DrawPlayerHand(Action):
    COMMAND = "!draw"
    
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
        if self.GAMESTATE.getCurrStage() == STAGES.DRAW:
            if not self.GAMESTATE.getPlayer(playerNumber).handInvisible: # if their hand is empty
                hand = self.GAMESTATE.drawPlayerHand(playerNumber)
                response.append("You drew: " + str(hand))
                response.append("Player" + str(playerNumber) + " has drawn: " + str(hand))
                
                if self.GAMESTATE.areAllHandsDealt():
                    self.GAMESTATE.moveToNextStage()
            else: # they already have a hand
                response.append("Sorry, you already have your hand!")
        else:
            response.append("Sorry, we're not drawing hands right now!")
        return response
