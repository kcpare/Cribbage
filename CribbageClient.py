# Kathryn Pare
# Cribbage Game Client (A file run by a player in order to play the game)

# CribbageClient connects and communicates with a running CribbageServer for information on how to set up the game
# Please note that the conventions for using select() to monitor multiple sockets are courtesy of Doug Hellmann: https://pymotw.com/2/select/

from ast import literal_eval
from Cribbage import CurrPlayer
import select
import socket
import sys
import queue

class CribbageClient:
    '''A class that can be run by a player to connect to the game'''

    # ---------------------------------------- Class Variables ---------------------------------------- #
    SERVER_IP_ADDRESS = '10.0.0.1' 
    SERVER_PORT = 2000

    # -------------------- Constructor -------------------- #
    def __init__(self):
        self.connect()

    # -------------------- Methods -------------------- #
    # Connects to Server
    def connect(self):
        # Please note: The useage of the select.select() function, and following three 'for' loops monitoring output from select() are courtesy of Doug Hellman
        # his instructions can be found at: https://pymotw.com/2/select/
        # For the client, select.select() is used to implement a nonblocking socket by forcing the program to take breaks to read from and write to the server as well as
            # listening to the player's actions by forcing the program to (potentially) read once, (potentially) write once, and (potentially) listen once, going in a cycle
        
        # Keeping track of the state of the game (will change if the users wants to exit)
        self.status = 'joining'        

	    # connecting to Server
        print("Client: Connecting to Cribbage Server")
        self.playerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.playerSocket.connect((self.__class__.SERVER_IP_ADDRESS, self.__class__.SERVER_PORT))
        self.playerSocket.setblocking(0)

        # Creating list of input sockets, output sockets, and a queue for outgoing messages as well as standard input
        self.inputs = [self.playerSocket, sys.stdin]
        self.outputs = []
        self.messageQueues = {}
        self.messageQueues[self.playerSocket] = queue.Queue()

        self.listen()

    # Listens for input from server
    def listen(self):
        while self.inputs: # empty lists evaluate to false in python  
            readable, writeable, exceptional = select.select(self.inputs, self.outputs, self.inputs)

            #if not (readable or writeable or exceptional):
                #print("No messages to receive or send. Listening to player actions instead")
                #
                # pass back to event listeners (or implement using select.select()?)
                #
            for r in readable:
                if r is sys.stdin: 
                    userInput = r.readline().strip()
                    self.messageQueues[self.playerSocket].put(userInput)
                    if self.playerSocket not in self.outputs:
                        self.outputs.append(self.playerSocket)
                    if userInput == 'exit':
                        self.status = 'exit'
                else:   
                    message = r.recv(1024)
                    if message: # if message is not empty
                        messageStr = message.decode()
                        self.handleMessage(messageStr)

                    else: # if message empty
                        print("Client: Received empty message from server - interpreting as exception. Closing connection with server")
                        self.disconnect()

            for w in writeable: 
                try:
                    nextMessage = self.messageQueues[w].get_nowait()
                except queue.Empty:
                    # stop checking for messages for them
                    self.outputs.remove(w)
                else:
                    if nextMessage == 'exit': # if we're shutting down the connection per user request
                        w.send(''.encode()) #send nothing to tell server to disconnect
                        print("Client: Exiting game")
                        self.disconnect()
                    else:
                        w.send(nextMessage.encode())
                    
            for e in exceptional: 
                print("Client: Due to an exception, closing connection with server ", e.getpeername())
                self.disconnect()
        sys.exit()

    # -------------------- Helper Functions -------------------- #
    # Disconnects player from socket and removes monitoring of sys.stdin (standard input)
    def disconnect(self):
        self.inputs.remove(self.playerSocket)
        if self.playerSocket in self.outputs:
            self.outputs.remove(self.playerSocket)
        del self.messageQueues[self.playerSocket]
        self.playerSocket.close()
        self.inputs.remove(sys.stdin) 

    def handleMessage(self, response):
        if response[0] == '>': # it's message from another player
            print(response[1:])

        else: # it's a message from the server that does not require action by the player's program
            print("Server:", response)


# -------------------- main -------------------- #
if __name__ == '__main__':
    cc = CribbageClient()

        

