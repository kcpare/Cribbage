# Kathryn Pare
# COMP 4911
# Term Project: Cribbage Server
# March 14, 2020

# Please note that the conventions for using select() to monitor multiple sockets are courtesy of Doug Hellmann: https://pymotw.com/2/select/

from Cribbage import Deck
from Cribbage import Player
from GameState import GameState
from PlayerActions.ActionFactory import ActionFactory
import select
import socket
import sys 
import queue

class CribbageServer:
    '''A server to faciliate a game of cribbage for 2-4 clients'''
    
    # -------------------- Class Variables -------------------- #
    SERVER_IP_ADDRESS = '10.0.0.1' # we'll want to make this dynamic in the future
    SERVER_PORT = 2000

    # -------------------- Constructor -------------------- #
    def __init__(self):
        # -------------------- Setting up server housekeeping for the game -------------------- #
        self.GAMESTATE = GameState()

        # Dictionaries of possible actions by the player
        #   Where the key is the action command typed by the player and the value is a function that will validate the action 
        ACTION_FACTORY = ActionFactory(self.GAMESTATE)
        self.PLAYER_ACTIONS = ACTION_FACTORY.getPlayerActions()

        # a list of the ip addresses of players, in order of their joining (and thus assigned number)
        self.PLAYERS_IP = ["Empty"] # Includes an empty entry in order for players to index starting at 1

        self.startServer()

    # -------------------- Methods -------------------- #

    # Setting up the server to connect with players #
    def startServer(self):
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

        listen(serverSocket)

    # Start listening for player input
    def listen(self, serverSocket):
        # Please note: Setting up a server to accept and handle players during a cribbage game
        # The useage of the select.select() function, and following three 'for' loops monitoring output from select() are courtesy of Doug Hellman
        # his instructions can be found at: https://pymotw.com/2/select/

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
                            desiredAction = messageStr.split()[0]
                            actionLength = len(desiredAction)
                            playerInput = messageStr[actionLength + 1:]
                            print("SERVER: type of playerInput:", type(playerInput))
                            print("SERVER: desiredAction = ", desiredAction, " and playerInput are ", playerInput)
                            responseBack, broadcast, responseAll = self.handleMessage(desiredAction, playerInput, currPlayerNumber)

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
    
    # -------------------- Helper functions -------------------- #
    # Takes in a desired action by a player and that player's number
    # Determines whether the action is valid and returns the appropriate response
    # Returns three values: (String) responseBack, (boolean) broadcast, (String) responseOthers
    #   Where the responseBack is the string to send back to the player who messaged,
    #   broadcast determines whether it is necessary to send information to other palyers
    #   and responseOthers is the string sent to other players (if necessary)
    def handleMessage(self, desiredAction, playerInput, playerNumber):
        # setting defaults
        responseBack = ''
        broadcast = False 
        responseOthers = ''

        f = self.PLAYER_ACTIONS.get(desiredAction) # a function that will validate the action is returned
        if f is not None: # if the desiredAction was a known action
            action = f(playerNumber, playerInput) # a list is returned with information to send out to player(s)
                
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

# -------------------- 'Main' Function -------------------- #
if __name__ == '__main__': # this will be true only for the file directly run (any imported modules with similar statements will not have theirs run)
    cServer = CribbageServer()

