import time

from PyQt5.QtWidgets import (QWidget,
                             QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QMessageBox)
from frontend.getAllClientsThread import getAllClientsThread

class Invite(QWidget):

    def __init__(self, client,groupId,groupOwner,previousScreen,thread):
        super().__init__()
        self.initUI(client,groupId,groupOwner,previousScreen,thread)

    def initUI(self, client,groupId,groupOwner,previousScreen,thread):

        self.client = client
        self.groupId = groupId
        self.groupOwner = groupOwner
        self.groupChat = previousScreen
        self.groupChatThread = thread

        inviteBtn = QPushButton('Invite', self)
        inviteBtn.resize(inviteBtn.sizeHint())
        inviteBtn.clicked.connect(self.invite)

        cancelBtn = QPushButton('Cancel', self)
        cancelBtn.resize(cancelBtn.sizeHint())
        cancelBtn.clicked.connect(self.close)

        self.remainingClients = []
        self.allClientThread = getAllClientsThread(self.client)
        self.allClientThread.allClients.connect(self.renderClientNotInGroup)
        self.allClientThread.start()

        hbox = QHBoxLayout()
        hbox.addWidget(inviteBtn)
        hbox.addWidget(cancelBtn)
        vbox = QVBoxLayout()
        self.otherClients = QListWidget()
        vbox.addWidget(QLabel("Connected Clients"))
        vbox.addWidget(self.otherClients)
        vbox.addLayout(hbox)

        self.setWindowTitle('Chatting Program')
        pos = self.groupChat.geometry()
        self.setGeometry(pos.left(),pos.top(),650, 800)
        self.setLayout(vbox)

    def renderClientNotInGroup(self,allClients):
        clientList = allClients[0]

        remainingClients = []

        for i in range(len(list(clientList))):
            inGroup = False
            key = list(clientList)[i]
            for id in clientList[key]:
                if(id == self.groupId):
                     inGroup = True
                     break
            if(inGroup == False):
                remainingClients.append(key)

        if(len(self.remainingClients) != len(remainingClients)):
             self.otherClients.clear()
             self.remainingClients = remainingClients
             for client in remainingClients:
                 self.otherClients.addItem(str(client[2]))

    def invite(self):
        self.allClientThread.stop()
        time.sleep(0.3)
        index = self.otherClients.currentRow()
        if(index == -1):
            msg_box = QMessageBox(QMessageBox.Warning, "Warning", "Please choose person first")
            pos = self.geometry()
            left = pos.left()
            top = pos.top()
            msg_box.setGeometry(left + 100, top + 200, 200, 300)
            msg_box.exec_()
        else:
            clientInfo = self.remainingClients[index]
            self.client.sendInvitation(self.groupId,clientInfo)
            msg_box = QMessageBox(QMessageBox.Information, "Information", "Send invitation to "+str(clientInfo[2]))
            pos = self.geometry()
            left = pos.left()
            top = pos.top()
            msg_box.setGeometry(left + 100, top + 200, 200, 300)
            msg_box.exec_()

        self.allClientThread.restart()
        self.allClientThread.start()

    def close(self):
        self.allClientThread.stop()
        time.sleep(0.5)
        self.hide()
        self.groupChat.show()
        self.groupChatThread.restart()
        self.groupChatThread.start()
