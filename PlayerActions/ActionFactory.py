# Kathryn Pare
# Cribbage Game State

from .Actions.StartGame import StartGame
from .Actions.DrawPlayerHand import DrawPlayerHand
from .Actions.PlayPlayerHand import PlayPlayerHand
from .Actions.CountPlayerHand import CountPlayerHand
from .Actions.DisplayPoints import DisplayPoints

class ActionFactory:
    '''ActionFactory holds all possible player actions'''

    # -------------------- Class Variables -------------------- #
    # Dictionaries of possible actions by the player
    #   In form of key: value pair, where the key is the action command and the value is a function that will validate the action 
    PLAYER_ACTIONS = {}

    # -------------------- Constructor -------------------- #
    def __init__(self, gameState):
         actions = []
         actions.append(StartGame(gameState))
         actions.append(DrawPlayerHand(gameState))
         actions.append(PlayPlayerHand(gameState))
         actions.append(CountPlayerHand(gameState))
         actions.append(DisplayPoints(gameState))
         # please add new actions here

         self.initializePlayerActions(actions)

    # -------------------- Methods -------------------- #
    
    # Takes in a list of Actions
    # For each Action, enters their command as a key in PLAYER_ACTIONS dictionary and their execute() function as the corresopnding value
    def initializePlayerActions(self, actionList):
        for action in actionList:
            # enter the new key: value pair
            self.__class__.PLAYER_ACTIONS[action.getActionCommand()] = action.execute
        pass
    
    def getPlayerActions(self):
        return self.__class__.PLAYER_ACTIONS
