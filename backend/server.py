
import select
import socket
import sys
import signal
import argparse
import ssl

from utils import *
from datetime import datetime

SERVER_HOST = 'localhost'

class Server(object):

    def __init__(self, port, backlog=5):
        self.clients = 0

        # use client channel to get the client info (address[0],address[1], name)
        self.clientmap = {}
        # all clients is the map, the key is the info of the client, value is the array which contains
        # the group Id which are joined by this client
        self.allClients = {}

        self.groups = 0
        # this is a map, the key is the groud id ,value is the owner
        self.groupOwners = {}

        #use client info to get client channel
        self.clientSockets = {}

        # all clients connection time, key is client, value is connection time
        self.allClientsTime = {}

        # all clients invitation info
        self.clientsInvitation ={}

        self.outputs = []  # list output sockets


        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.context.load_cert_chain("new.pem", "private.key")
        self.context.load_verify_locations('new.pem')
        self.context.set_ciphers('AES128-SHA')

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((SERVER_HOST, port))
        self.server.listen(backlog)
        self.server = self.context.wrap_socket(self.server, server_side=True)

        # Catch keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)

        print(
            f'Server (IP Address: {SERVER_HOST}) listening to port: {port} ...')

    def sighandler(self):
        """ Clean up client outputs"""
        print('Shutting down server...')

        # Close existing client sockets
        for output in self.outputs:
            output.close()

        self.server.close()

    def get_client_name(self, client):
        """ Return the name of the client """
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return '@'.join((name, host))

    def run(self):
        inputs = [self.server]
        self.outputs = []
        running = True
        while running:
            try:
                readable, writeable, exceptional = select.select(
                    inputs, self.outputs, [])
            except select.error as e:
                break

            for sock in readable:
                sys.stdout.flush()
                if sock == self.server:
                    # handle the server socket
                    client, address = self.server.accept()
                    # get current client connection time
                    self.connectTime = datetime.now()
                    print(
                        f'Chat server: got connection {client.fileno()} from {address}')
                    # Read the login name
                    cname = receive(client).split('NAME: ')[1]

                    # Compute client name and send back
                    self.clients += 1
                    send(client, f'CLIENT: {str(address)}')
                    inputs.append(client)
                    self.clientmap[client] = (address, cname)

                    self.allClients[(address[0], address[1], cname)] = []
                    self.allClientsTime[(
                        address[0], address[1], cname)] = self.connectTime
                    self.clientSockets[(
                        address[0], address[1], cname)] = client
                    self.clientsInvitation[(address[0], address[1], cname)] = []
                    self.outputs.append(client)

                else:
                    # handle all other sockets
                    try:
                        data = receive(sock)
                        if data:
                            if type(data) == int:
                                if (data == 1):  # 1 is means the client want to get all clients
                                    send(
                                        sock, [self.allClients,self.allClientsTime,self.groupOwners,self.clientsInvitation])
                                if (data == 2):  # 2 is means the client want to create a new group
                                    self.groups += 1
                                    clientInfo = self.clientmap[sock]
                                    self.allClients[(clientInfo[0][0], clientInfo[0][1], clientInfo[1])].append(
                                        self.groups)
                                    self.groupOwners[self.groups] = (clientInfo[0][0],clientInfo[0][1],clientInfo[1])
                            if type(data) == tuple:
                                # add client to group
                                if type(data[0])== int:
                                    groupId = data[0]
                                    self.allClients[data[1]].append(groupId)
                                elif type(data[0]) == tuple:# send invitation
                                    groupId = data[1]
                                    self.clientsInvitation[data[0]].append(groupId)
                            if type(data)== list:
                                if(type(data[2])==tuple):# one to one
                                    clientKey = data[2]
                                    if(self.allClients.__contains__(clientKey)):
                                        clientToSend = self.clientSockets[data[2]]
                                        send(clientToSend, data)
                                    else:
                                        clientSelf = self.clientSockets[data[1]]
                                        newData = [data[0],data[1],data[2],f"{data[2][2]} is left the room"]
                                        send(clientSelf,newData)

                                else: # one to group
                                  clientInGroup = []
                                  groupId = data[2]
                                  for i in range(len(list(self.allClients))):
                                      key = list(self.allClients)[i]
                                      groupIds = self.allClients[key]
                                      for id in groupIds:
                                          if(id==groupId):
                                              targetClient = self.clientSockets[key]
                                              if(targetClient != sock):
                                                clientInGroup.append(targetClient)
                                              break;
                                  for client in clientInGroup:
                                      send(client,data)

                        else:
                            print(f'Chat server: {sock.fileno()} hung up')
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock)
                            self.outputs.remove(sock)
                            clientInfo = self.clientmap[sock]
                            keyToRemove = (
                                clientInfo[0][0], clientInfo[0][1], clientInfo[1])
                            self.clientmap.pop(sock)
                            self.allClients.pop(keyToRemove)
                            self.clientSockets.pop(keyToRemove)
                            keyRemove = []
                            for i in range(len(self.groupOwners)):
                                key = list(self.groupOwners)[i]
                                if(self.groupOwners[key] == keyToRemove):
                                    keyRemove.append(key)
                            for val in keyRemove:
                                self.groupOwners.pop(val)
                    except socket.error as e:
                        # Remove
                        inputs.remove(sock)
                        self.outputs.remove(sock)
                        self.clients -= 1
                        clientInfo = self.clientmap[sock]
                        keyToRemove = (
                            clientInfo[0][0], clientInfo[0][1], clientInfo[1])
                        self.clientmap.pop(sock)
                        self.allClients.pop(keyToRemove)
                        self.clientSockets.pop(keyToRemove)
                        keyRemove = []
                        for i in range(len(self.groupOwners)):
                            key = list(self.groupOwners)[i]
                            if (self.groupOwners[key] == keyToRemove):
                                keyRemove.append(key)
                        for val in keyRemove:
                            self.groupOwners.pop(val)
        self.server.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='chat program')
    parser.add_argument('--name', action="store", dest="name", required=True)
    parser.add_argument('--port', action="store",
                        dest="port", type=int, required=True)
    given_args = parser.parse_args()
    port = given_args.port
    name = given_args.name

    server = Server(port)
    server.run()
