# -*- coding: utf-8 -*-

from socket import *
import thread

class Client(object):

    def __init__(self, name, address, socket):
        self.name = name
        self.address = address
        self.socket = socket
        self.channel = ""
    
    def setChannel(self, channel):
        self.channel = channel

    def getChannel(self):
        return self.channel

class Channel(object):

    def __init__(self, name):
        self.name = name
        self.subscriber = []

    def addSubsciber(self, client):
        self.subscriber.append(client)

    def deleteSubsciber(self, client):
        self.subscriber.remove(client)

MESSAGE_LENGTH = 200

#### Server messages ####

# The client sent a control message (a message starting with "/") that doesn't exist
# (e.g., /foobar).
SERVER_INVALID_CONTROL_MESSAGE = \
  "{} is not a valid control message. Valid messages are /create, /list, and /join."

# Message returned when a client attempts to join a channel that doesn't exist.
SERVER_NO_CHANNEL_EXISTS = "No channel named {0} exists. Try '/create {0}'?"

# Message sent to a client that uses the "/join" command without a channel name.
SERVER_JOIN_REQUIRES_ARGUMENT = "/join command must be followed by the name of a channel to join."

# Message sent to all clients in a channel when a new client joins.
SERVER_CLIENT_JOINED_CHANNEL = "{0} has joined"

# Message sent to all clients in a channel when a client leaves.
SERVER_CLIENT_LEFT_CHANNEL = "{0} has left"

# Message sent to a client that tries to create a channel that doesn't exist.
SERVER_CHANNEL_EXISTS = "Room {0} already exists, so cannot be created."

# Message sent to a client that uses the "/create" command without a channel name.
SERVER_CREATE_REQUIRES_ARGUMENT = \
  "/create command must be followed by the name of a channel to create"

# Message sent to a client that sends a regular message before joining any channels.
SERVER_CLIENT_NOT_IN_CHANNEL = \
  "Not currently in any channel. Must join a channel before sending messages."

serverName = 'localhost'
serverPort = 12001
clients = []
channels = []

server_socket = socket(AF_INET,SOCK_STREAM)
server_socket.bind((serverName, serverPort))
server_socket.listen(5)

def checkOperation(message):
    if(message[0] == '/'):
        return True
    else:
        return False


def parseOperation(message):
    if(message[1:5] == 'list'):
        return 'list'
    elif(message[1:5] == 'join'):
        return 'join'
    elif(message[1:7] == 'create'):
        return 'create'
    else:
        return message.split()[0]
    

def parseChannelName(client, message):
    try:
        channel = message.split()[1]
    except:
        print message.split()[0]
        if(message.split()[0] == '/join'):
            client.socket.send(SERVER_JOIN_REQUIRES_ARGUMENT)
            print SERVER_JOIN_REQUIRES_ARGUMENT
        elif(message.split()[0] == '/create'):
            client.socket.send(SERVER_CREATE_REQUIRES_ARGUMENT)
            print SERVER_CREATE_REQUIRES_ARGUMENT
        return
    return channel

def returnChannelList(socket):
    channelMessage = ''
    for channel in channels:
        channelMessage = channelMessage + channel.name + '\n'
    print channelMessage
    socket.send(channelMessage)

def createChannel(client, socket, channelName):
    print('creating channel...')
    newChannel = Channel(channelName)
    newChannel.addSubsciber(client)
    client.setChannel(newChannel)
    if channels.count(newChannel) > 0 :
        client.socket.send(SERVER_CHANNEL_EXISTS.format(newChannel))
        return
    channels.append(newChannel)

def broadcastMessage(client, message):
    channel = client.getChannel()
    if(channel == ""):
        client.socket.send(SERVER_CLIENT_NOT_IN_CHANNEL)
        return
    for subscriber in channel.subscriber:
        subscriber.socket.send(message)

def joinChannel(channelName, client):
    channelObj = ""
    for channel in channels:
        if channel.name == channelName:
            channelObj = channel
        else:
            client.socket.send(SERVER_NO_CHANNEL_EXISTS.format(channelName))
            return
    broadcastMessage(client, SERVER_CLIENT_LEFT_CHANNEL.format(client.name))
    client.setChannel(channelObj)
    broadcastMessage(client, SERVER_CLIENT_JOINED_CHANNEL.format(client.name))
    channelObj.subscriber.append(client)

def listenClient(client):
    while True:
        message = client.socket.recv(1024)
        print("Client: " + client.name)
        print("Message: " + message)
        if checkOperation(message):
            operation = parseOperation(message)
            if(operation == 'list'):
                print 'list operation'
                returnChannelList(client.socket)
            elif(operation == 'create'):
                print 'create operation'
                channelName = parseChannelName(client, message)
                if (channelName != None):
                    createChannel(client, client.socket, channelName)
            elif(operation == 'join'):
                print 'join operation'
                channelName = parseChannelName(client, message)
                if (channelName != None):
                    joinChannel(channelName, client)
            else:
                print 'worong operation'
                client.socket.send(SERVER_INVALID_CONTROL_MESSAGE.format(operation))
        else:
            broadcastMessage(client, message)

    print 'end'
            

while True:
    connectionSocket, addr = server_socket.accept()
    sentence = connectionSocket.recv(1024).decode()
    clientInfo = sentence.split()
    client = Client(clientInfo[0], addr, connectionSocket)
    clients.append(client)
    print('new client')
    thread.start_new_thread(listenClient, (client, ))








