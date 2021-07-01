# Kathryn Pare
# Cribbage Game State

from .Action import Action
from GameState import GameState
from GameState import STAGES

# StartGame implements Action to define how a player can start the game
class StartGame(Action):
    COMMAND = "!startgame"
    
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
        if self.GAMESTATE.getCurrStage() == STAGES.START:
            if (self.GAMESTATE.getNumberOfPlayers() < 2): # if we don't have at least 2 players
                response.append("Sorry, not enough players! Please find an opponent.")
            else:
                response.append("Welcome! Game is starting.")
                response.append("Welcome! Player" + str(playerNumber) + " has started the game.")
                self.GAMESTATE.moveToNextStage()
        else:
            response.append("Game has already started!")
        return response
