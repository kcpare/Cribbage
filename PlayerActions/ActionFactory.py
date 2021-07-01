# Kathryn Pare
# Cribbage Game State

import StartGame
import DrawPlayerHand
import PlayPlayerHand
import CountPlayerHand

# ActionFactory holds all possible player actions
# When one needs to add a new action to the game, please add it to the list actions
class ActionFactory:
    # Dictionaries of possible actions by the player
    #   In form of key: value pair, where the key is the action command and the value is a function that will validate the action 
    PLAYER_ACTIONS = {}

    def __init__(self):
         actions = []
         actions.append(StartGame())
         actions.append(DrawPlayerHand())
         actions.append(PlayPlayerHand())
         actions.append(CountPlayerHand())
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