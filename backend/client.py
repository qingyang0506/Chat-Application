
import socket
import sys
import ssl
import threading

from backend.utils import send,receive

SERVER_HOST = 'localhost'

stop_thread = False


class Client():
    """ A command line chat client using select """

    def __init__(self, name, port, host=SERVER_HOST):
        self.name = name
        self.connected = False
        self.host = host
        self.port = port

        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)

        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock = self.context.wrap_socket(
                self.sock, server_hostname=host)

            self.sock.connect((host, self.port))
            print(f'Now connected to chat server@ port {self.port}')
            self.connected = True

            # Send my name...
            send(self.sock, 'NAME: ' + self.name)
            data = receive(self.sock)

            # Contains client address, set it
            ipAndPort = data.split('CLIENT: ')[1][1:-1].split(", ")
            self.addr = ipAndPort[0]
            self.portAddr = int(ipAndPort[1])

            threading.Thread(args=(self,)).start()

        except socket.error as e:
            print(f'Failed to connect to chat server @ port {self.port}')
            sys.exit(1)

    def cleanup(self):
        send(self.sock, False)
        """Close the connection and wait for the thread to terminate."""
        self.sock.close()

    def getAllClients(self):
        send(self.sock, 1)
        data = receive(self.sock)
        return data

    def sendAllClientsSignal(self):
        send(self.sock,1)

    def createNewGroup(self):
        send(self.sock, 2)

    def sendMessage(self, message):
        send(self.sock, message)

    def recieveData(self):
        data = receive(self.sock)
        return data

    def getMyName(self):
        return self.name

    def getInfo(self):
        return (self.addr.replace("'",""),self.portAddr,self.name)

    def addToGroup(self,groupId):
        send(self.sock,(groupId,self.getInfo()))

    def sendInvitation(self,groupId,clientInfo):
        send(self.sock,(clientInfo,groupId))