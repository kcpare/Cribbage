# Kathryn Pare
# Cribbage Game State

from .StartGame import StartGame
from .DrawPlayerHand import DrawPlayerHand
from .PlayPlayerHand import PlayPlayerHand
from .CountPlayerHand import CountPlayerHand
from .DisplayPoints import DisplayPoints

# ActionFactory holds all possible player actions
# When one needs to add a new action to the game, please add it to the list actions
class ActionFactory:
    # Dictionaries of possible actions by the player
    #   In form of key: value pair, where the key is the action command and the value is a function that will validate the action 
    PLAYER_ACTIONS = {}

    def __init__(self, gameState):
         actions = []
         actions.append(StartGame(gameState))
         actions.append(DrawPlayerHand(gameState))
         actions.append(PlayPlayerHand(gameState))
         actions.append(CountPlayerHand(gameState))
         actions.append(DisplayPoints(gameState))
         # please add new actions here

         self.initializePlayerActions(actions)

    # Takes in a list of Actions
    # For each Action, enters their command as a key in PLAYER_ACTIONS dictionary and their execute() function as the corresopnding value
    def initializePlayerActions(self, actionList):
        for action in actionList:
            # enter the new key: value pair
            self.__class__.PLAYER_ACTIONS[action.getActionCommand()] = action.execute
        pass
    
    def getPlayerActions(self):
        return self.__class__.PLAYER_ACTIONS
