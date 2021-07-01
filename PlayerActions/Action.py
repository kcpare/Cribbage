# Kathryn Pare
# Cribbage Game State

from abc import ABC, abstractmethod
      
class Action(ABC):
    '''An interface to define classes which represent and execute valid actions a player can take'''
    
    # The command associated with their action (ex. !draw, !play, !count). By convention, these are prefaced with an exclaimation mark
    @abstractmethod
    def getActionCommand(self):
        pass

    # An algorithm to validate execute the action along with any player input following the action, which takes in the player number
    # - This returns a list of either:
    # -- length 1 for a (string) message back to that player, or
    # -- length 2 for a (string) message back to that player and a (string) message for all other players
    @abstractmethod
    def execute(self, playerNumber, input):
        pass
