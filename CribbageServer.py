# Kathryn Pare
# COMP 4911
# Term Project: Cribbage Server
# March 14, 2020

# Please note that the conventions for using select() to monitor multiple sockets are courtesy of Doug Hellmann: https://pymotw.com/2/select/

from Cribbage import Deck
from Cribbage import Player
from GameState import GameState
from GameState import STAGES
import select
import socket
import sys 
import queue

class CribbageServer:
    '''A server to faciliate a game of cribbage for 2-4 clients'''
    # ----- Class Variables ----- #
    SERVER_IP_ADDRESS = '10.0.0.1' # we'll want to make this dynamic in the future
    SERVER_PORT = 2000

    # ----- Starting Server ----- #
    # Setting up a server to accept and handle players during a cribbage game
    # The useage of the select.select() function, and following three 'for' loops monitoring output from select() are courtesy of Doug Hellman
        # his instructions can be found at: https://pymotw.com/2/select/
    def __init__(self):
        # ----- Setting up server housekeeping for the game ----- #
        self.GAMESTATE = GameState()

        # Dictionaries of possible actions by the player
        #   In form of key: value pair, where the value is a function that will validate the action 
        self.PLAYER_ACTIONS = { 
            'draw': self.drawPlayerHand,
            'start game': self.startGame,
            'play': self.playPlayerHand,
            'points': self.displayPoints,
        } 

        # a list of the ip addresses of players, in order of their joining (and thus assigned number)
        self.PLAYERS_IP = ["Empty"] # Includes an empty entry in order for players to index starting at 1

        # ----- setting up the server to connect with players ----- # 

        # creating a socket to listen for joining players
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # we want IPv4 and a TCP socket
        serverSocket.setblocking(0)
        serverSocket.bind((self.__class__.SERVER_IP_ADDRESS, self.__class__.SERVER_PORT))
        serverSocket.listen(self.GAMESTATE.__class__.MAX_PLAYERS) # will prevent us from accepting any more than MAX_PLAYER number of connections
        print("SERVER: Ready!")

        # Creating list of input sockets, output sockets, and a queue for outgoing messages
        self.inputs = [serverSocket]
        self.outputs = []
        self.messageQueues = {}

        while self.inputs: #empty lists evaluate to false in python
            print("SERVER: Waiting for connection...")
            readable, writeable, exceptional = select.select(self.inputs, self.outputs, self.inputs)

            # handling sockets from select
            for r in readable: # handling sockets with incoming data
                if r is serverSocket: # a player is joining
                    connectionSocket, clientAddr = r.accept()
                    connectionSocket.setblocking(0) # allowing them to not have to wait for our response
                    self.inputs.append(connectionSocket) # adding them to the list to monitor for incoming data
                    self.messageQueues[connectionSocket] = queue.Queue() # creating an outgoing message queue for this socket

                    playerNum = len(self.PLAYERS_IP)
                    print("SERVER: Accepted a new player from ", clientAddr, ". They will be Player", playerNum)
                    self.PLAYERS_IP.append(clientAddr) # adding the player to our list of players
                    self.GAMESTATE.addPlayer(Player(playerNum))

                    # Sending out welcome messages
                    self.queueMessage(connectionSocket, "You have joined the game! Welcome! You are Player" + str(playerNum)) # to this player
                    for playerSocket in self.inputs: # to everyone else
                        if (playerSocket is not connectionSocket) and (playerSocket is not serverSocket):
                            self.queueMessage(playerSocket, "Player" + str(playerNum) + " has joined!")

                else: # message from an already connected player
                    message = r.recv(1024)
                    currPlayerNumber = self.PLAYERS_IP.index(r.getpeername())
                    if message: # if message is not empty
                        messageStr = message.decode()
                        print("SERVER: Received message: \'", messageStr, "\' from Player", currPlayerNumber)
                        if messageStr[0] == "!": # if the message was a request to the server for an action (ex. drawing a card, i.e. !draw)
                            desiredAction = messageStr[1:]
                            responseBack, broadcast, responseAll = self.handleMessage(desiredAction, currPlayerNumber)

                            # send a message back to the player
                            self.queueMessage(r, responseBack)

                            # send a message to every other player, if needed
                            if broadcast: 
                                for playerSocket in self.inputs:
                                    if (playerSocket is not r) and (playerSocket is not serverSocket):
                                        self.queueMessage(playerSocket, responseAll)

                        else: # the message was text to other players (a conversation) and needs to be broadcasted
                            for playerSocket in self.inputs: 
                                    if (playerSocket is not r) and (playerSocket is not serverSocket):
                                        self.queueMessage(playerSocket, ">Player" + str(currPlayerNumber) + ": " + messageStr)

                    else: # no data means the player has likely disconnected
                        print("SERVER: Player", currPlayerNumber, "has disconnected. Closing connection with player")
                        self.disconnectPlayer(r)

            for w in writeable: # handling sockets which have become writeable
                try:
                    nextMessage = self.messageQueues[w].get_nowait()
                except queue.Empty:
                    # stop checking for messages for them
                    print("SERVER: No more messages for Player", self.PLAYERS_IP.index(w.getpeername()))
                    self.outputs.remove(w)
                else:
                    print("SERVER: Sending message: \'", nextMessage, "\' to player", self.PLAYERS_IP.index(w.getpeername()))
                    w.send(nextMessage.encode())

            for e in exceptional: # handling any sockets with exceptions (by closing them)
                print("SERVER: Due to an exception, closing connection with Player ", self.PLAYERS_IP.index(e.getpeername()))
                self.disconnectPlayer(e)

        serverSocket.close()
        sys.exit()
    
    # ----- Helper functions ----- #
    # Takes in a desired action by a player and that player's number
    # Determines whether the action is valid and returns the appropriate response
    # Returns three values: (String) responseBack, (boolean) broadcast, (String) responseOthers
    #   Where the responseBack is the string to send back to the player who messaged,
    #   broadcast determines whether it is necessary to send information to other palyers
    #   and responseOthers is the string sent to other players (if necessary)
    def handleMessage(self, desiredAction, playerNumber):
        # setting defaults
        responseBack = ''
        broadcast = False 
        responseOthers = ''

        # preparing response
        if 'peg' in desiredAction: # if the player wanted to count their cards (this is dealt with specially bc following the command is user input)
            # checking whether they entered double digits
            if len(desiredAction) > 5: 
                action = self.countPlayerHand(playerNumber, int(desiredAction[4:6])) #only slice to 5th index, in case they entered words after (ex. !peg 12 points)
            elif len(desiredAction) == 5: # if they entered a single digit point count
                action = self.countPlayerHand(playerNumber, int(desiredAction[4]))
            else: # if they forgot to enter points
                action = ['Please enter the points you wish to count!']
        
            responseBack = action[0] # prepare message to send back to player
            if len(action) == 2: # if action has length 2, then it has a message for both the player who initiated it and everyone else
                broadcast = True
                responseOthers = action[1] # prepare response to everyone else
        else: # if it's not an action that requires input from the user
            f = self.PLAYER_ACTIONS.get(desiredAction) # a function that will validate the action is returned
        
            if f is not None: # if the desiredAction was a known action
                action = f(playerNumber) # a list is returned with information to send out to player(s)
                
                responseBack = action[0] # prepare message to send back to player
                if len(action) == 2: # if action has length 2, then it has a message for both the player who initiated it and everyone else
                    broadcast = True
                    responseOthers = action[1] # prepare response to everyone else
            else: # desiredAction wasn't in the dictionary
                responseBack = "Sorry! Not a valid action. Please try again."

        return responseBack, broadcast, responseOthers 

    # Takes in a player's socket, adds them to the list of output sockets if needed, and adds a message (string) to their queue
    def queueMessage(self, playerSocket, message):
        self.messageQueues[playerSocket].put(message)
        if playerSocket not in self.outputs:
            self.outputs.append(playerSocket)

    # Takes in a player's socket
    # Removes the players socket from our lists of things to monitor with select.select() and closes the player's socket
    def disconnectPlayer(self, playerSocket):
        if playerSocket in self.outputs:
            self.outputs.remove(playerSocket)
        num = self.PLAYERS_IP.index(playerSocket.getpeername())
        del self.PLAYERS_IP[num]
        self.GAMESTATE.removePlayer(num)
        self.inputs.remove(playerSocket)
        playerSocket.close()
        del self.messageQueues[playerSocket]

    # ----- Methods to validate desired actions by players ----- #
    # Each takes in the number of player who intiated the action
    # Each returns a list of either:
    #   length 1 for a (string) message back to that player, or
    #   length 2 for a (string) message back to that player and a (string) message for all other players
    # As appropriate, some shifts in the game stage may also be made

    def startGame(self, playerNumber):
        response = []
        if self.GAMESTATE.getCurrStage() == STAGES.START:
            if (len(self.PLAYERS_IP) - 1) < 2: # if we don't have at least 2 players
                response.append("Sorry, not enough players! Please find an opponent.")
            else:
                response.append("Welcome! Game is starting.")
                response.append("Welcome! Player" + str(playerNumber) + " has started the game.")
                self.GAMESTATE.moveToNextStage()
        else:
            response.append("Game has already started!")
        return response

    def drawPlayerHand(self, playerNumber):
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

    def playPlayerHand(self, playerNumber):
        response = []
        if self.GAMESTATE.getCurrStage() == STAGES.PLAY:
            if self.GAMESTATE.getPlayer(playerNumber).handInvisible: # if their hand has not already been played (is not empty)
                hand = self.GAMESTATE.playPlayerHand(playerNumber)
                response.append("You played you hand: " + str(hand))
                response.append("Player" + str(playerNumber) + " has played: " + str(hand))

                # testing whether we need to switch to next stage
                if self.GAMESTATE.areAllHandsPlayed():
                    self.GAMESTATE.moveToNextStage()
            else: # if their hand has already been played
                response.append("Sorry, you already played your hand!")
        else:
            response.append("Sorry, we're not playing hands right now!")
        return response

    def countPlayerHand(self, playerNumber, points):
        response = []
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

    def displayPoints(self, playerNumber):
        response = ['']
        for i in range(self.GAMESTATE.getNumberOfPlayers()): # we have an extra "empty" player in order to start indexing at 1
            if (i+1) == playerNumber: # their points
                response[0] = response[0] + '\nYou   : ' + str(self.GAMESTATE.getPlayer(i+1).points) + ' points'
            else: # everyone else's points
                response[0] = response[0] + '\nPlayer' + str(i+1) + ': ' + str(self.GAMESTATE.getPlayer(i+1).points) + ' points'

        return response

# ----- 'Main' Function ----- #
if __name__ == '__main__': # this will be true only for the file directly run (any imported modules with similar statements will not have theirs run)
    cServer = CribbageServer()

