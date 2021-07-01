# Kathryn Pare
# Cribbage Game State

from ..Action import Action
from GameState import GameState

# StartGame implements Action to define how a player can play their hand
class DisplayPoints(Action):
    COMMAND = "!points"

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
        response = ['']
        for i in range(self.GAMESTATE.getNumberOfPlayers()): # we have an extra "empty" player in order to start indexing at 1
            if (i+1) == playerNumber: # their points
                response[0] = response[0] + '\nYou   : ' + str(self.GAMESTATE.getPlayer(i+1).points) + ' points'
            else: # everyone else's points
                response[0] = response[0] + '\nPlayer' + str(i+1) + ': ' + str(self.GAMESTATE.getPlayer(i+1).points) + ' points'

        return response
