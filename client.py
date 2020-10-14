import thread
import threading
from socket import *
import sys


class BasicClient(object):

    def __init__(self, name, address, port):
        self.name = name
        self.address = address
        self.port = int(port)
        self.socket = socket(AF_INET, SOCK_STREAM)

        self.socket.connect((self.address, self.port))
        self.send(self.name)

    def send(self, message):
        self.socket.send(message)


class ListenStdIn(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            print('Listening to StdIn ...')
            sentence = raw_input('[Me] ')
            # add spaces to make sentence 200 characters
            if len(sentence) < 200:
                for x in range(200 - len(sentence)):
                    sentence = sentence + " "

            client.send(sentence)


class ListenServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            print('Listening to Server ...')
            sentence = client.socket.recv(1024)
            print (sentence.rstrip())


args = sys.argv
if len(args) != 4:
    print "Please supply a server address and port. # of args: " + repr(len(args))
    sys.exit()
print args[0]
client = BasicClient(args[1], args[2], args[3])

print "Client name: " + client.name
print "Address name: " + client.address
print "Port name: " + repr(client.port)

threads = []

inputThread = ListenStdIn()
serverThread = ListenServer()

inputThread.start()
serverThread.start()

threads.append(inputThread)
threads.append(serverThread)