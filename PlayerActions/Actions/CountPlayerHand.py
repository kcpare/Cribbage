# Kathryn Pare
# Cribbage Game State

from ..Action import Action
from GameState import GameState
from GameState import STAGES

class CountPlayerHand(Action):
    '''CountPlayerHand implements Action to define how a player can count their hand'''

    # -------------------- Class Variables -------------------- #
    COMMAND = "!count"

    # -------------------- Constructor -------------------- #
    def __init__(self, gameState):
        self.GAMESTATE = gameState

    # -------------------- Methods -------------------- #

    # The command associated with their action (ex. !draw, !play, !count). By convention, these are prefaced with an exclaimation mark
    def getActionCommand(self):
        return self.__class__.COMMAND

    # An algorithm to validate and execute the action along with any player input following the action, which takes in the player number
    # - This returns the server's 'response' back, which is a list of either:
    # -- length 1 for a (string) message back to that player, or
    # -- length 2 for a (string) message back to that player and a (string) message for all other players
    def execute(self, playerNumber, playerInput):
        response = []
        # check that input is not empty and is an integer
        if(not playerInput):
            response.append("Please remember to include a number of points you would like to count")
            return response
        elif(not self.isInt(playerInput)):
            response.append("Please remember to add a valid integer number of points")
            return response

        points = int(playerInput)

        if self.GAMESTATE.getCurrStage() == STAGES.COUNT: 
            if self.GAMESTATE.hasPlayedHand(playerNumber): # if they've played their hand
                if not self.GAMESTATE.hasCountedHand(playerNumber): # if they haven't yet counted their hand
                    self.GAMESTATE.addPointsToPlayer(playerNumber, points)
                    response.append("You gained " + str(points) + " points")
                    response.append("Player" + str(playerNumber) + " has gained " + str(points) + " points")

                    # testing whether we need to switch to next stage 
                    if self.GAMESTATE.areAllHandsCounted():
                        self.GAMESTATE.moveToNextStage()
                        self.GAMESTATE.resetBoard()
                else:
                    response.append("You've already counted your hand!")
            else:
                response.append("You need to play your hand first!")
        else:
            response.append("Sorry, we're not counting hands right now! ")
        return response

    # -------------------- Helper Functions -------------------- #
    def isInt(self, str):
        try:
            int(str)
            return True
        except ValueError:
            return False
