
from PyQt5.QtWidgets import (QWidget, QMessageBox,
                             QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QListWidget)
import time
from frontend.oneToOneChat import oneToOne
from frontend.GroupChat import GroupChat
from frontend.getAllClientsThread import getAllClientsThread
from datetime import datetime


class Connected(QWidget):

    def __init__(self, previousScreen, client):
        super().__init__()
        self.initUI(previousScreen, client)

    def initUI(self,  previousScreen, client):

        self.client = client
        self.connected = previousScreen
        self.clientList = {}
        self.groupOwner = {}
        self.invitation = []
        oneToOneBtn = QPushButton('1:1 Chat', self)
        oneToOneBtn.resize(oneToOneBtn.sizeHint())
        oneToOneBtn.clicked.connect(self.oneToOne)

        createBtn = QPushButton('Create', self)
        createBtn.resize(createBtn.sizeHint())
        createBtn.clicked.connect(self.createGroup)

        joinBtn = QPushButton('Join', self)
        joinBtn.resize(joinBtn.sizeHint())
        joinBtn.clicked.connect(self.toGroupChat)

        closeBtn = QPushButton('Close', self)
        closeBtn.resize(closeBtn.sizeHint())
        closeBtn.clicked.connect(self.close)

        hbox1 = QHBoxLayout()
        self.connectedClients = QListWidget()
        # start get all clients thread to update the connected client instancely
        self.allClientThread = getAllClientsThread(self.client)
        self.allClientThread.allClients.connect(
            self.renderClients)
        self.allClientThread.start()

        hbox1.addWidget(self.connectedClients)
        hbox1.addWidget(oneToOneBtn)

        vbox1 = QVBoxLayout()
        vbox1.addWidget(QLabel('Connected Clients'))
        vbox1.addLayout(hbox1)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(createBtn)
        vbox2.addWidget(joinBtn)

        hbox2 = QHBoxLayout()
        self.groupChats = QListWidget()
        self.selectedGroupIndex = self.groupChats.currentRow()
        hbox2.addWidget(self.groupChats)
        hbox2.addLayout(vbox2)

        vbox3 = QVBoxLayout()
        vbox3.addWidget(QLabel('Chat Rooms (Group Chat)'))
        vbox3.addLayout(hbox2)

        hbox3 = QHBoxLayout()
        hbox3.addStretch(1)
        hbox3.addWidget(closeBtn)

        vbox = QVBoxLayout()
        vbox.addLayout(vbox1)
        vbox.addLayout(vbox3)
        vbox.addLayout(hbox3)

        self.setWindowTitle('Chatting Program')
        pos = self.connected.geometry()
        self.setGeometry(pos.left(),pos.top(),650, 800)
        self.setLayout(vbox)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', 'Are you sure to quit?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def close(self):
        self.allClientThread.stop()
        time.sleep(0.5)
        self.client.cleanup()
        self.hide()
        self.connected.show()

    def createGroup(self):
        self.allClientThread.stop()
        time.sleep(0.5)
        self.client.createNewGroup()
        self.allClientThread.restart()
        self.allClientThread.start()

    def oneToOne(self):
        self.allClientThread.stop()
        index = self.connectedClients.currentRow()
        if(index == -1):
            msg_box = QMessageBox(QMessageBox.Warning, "warning", "Please choose people first")
            pos = self.geometry()
            left = pos.left()
            top = pos.top()
            msg_box.setGeometry(left+100,top+200,200,300)
            msg_box.exec_()
        else:
            clientToTalk = list(self.clientList)[index]
            if(clientToTalk[2]==self.client.getMyName()):
                msg_box = QMessageBox(QMessageBox.Warning, "warning","Can not chat with yourself")
                pos = self.geometry()
                left = pos.left()
                top = pos.top()
                msg_box.setGeometry(left + 100, top + 200, 200, 300)
                msg_box.exec_()
            else:
                time.sleep(0.5)
                self.window = oneToOne(self.client, clientToTalk, self,
                                       self.allClientThread)
                self.window.show()
                self.hide()

    def toGroupChat(self,groupId=0):
        if(groupId != 0):
            self.allClientThread.stop()
            time.sleep(0.5)
            self.client.addToGroup(groupId)
            self.window = GroupChat(self.client, groupId, self.groupOwner[groupId][2], self, self.allClientThread)
            self.window.show()
            self.hide()
        else:
            self.allClientThread.stop()
            time.sleep(0.3)
            index = self.groupChats.currentRow()
            if(index == -1):
                msg_box = QMessageBox(QMessageBox.Warning, "warning", "Please choose chat room first")
                pos = self.geometry()
                left = pos.left()
                top = pos.top()
                msg_box.setGeometry(left + 100, top + 200, 200, 300)
                msg_box.exec_()
            else:
                groupId = int(self.groupChats.currentItem().text().split(" ")[1])
                # judge whether this group have already exist the client
                isExist = False
                groupIds = self.clientList[self.client.getInfo()]
                for ids in groupIds:
                    if ids == groupId:
                        isExist = True
                        break
                if((isExist == False) & (self.client.getMyName() != self.groupOwner[groupId][2])):
                    self.client.addToGroup(groupId)
                    time.sleep(0.3)
                time.sleep(0.5)
                self.window = GroupChat(self.client,groupId,self.groupOwner[groupId][2],self,self.allClientThread)
                self.window.show()
                self.hide()

        
    def renderClients(self, allClients):
        clientList = allClients[0]
        allClientsTime = allClients[1]
        groupOwners= allClients[2]
        clientInvitation = allClients[3]

        currentInvitation = clientInvitation[self.client.getInfo()]

        if(len(currentInvitation)!=len(self.invitation)):
            self.invitation = currentInvitation

            currentGroupId = self.invitation[len(self.invitation)-1]

            self.box = QMessageBox(QMessageBox.Question,"Join",f"{self.client.name}, Do you want to join Room {currentGroupId} ?")

            yes = self.box.addButton('Yes', QMessageBox.YesRole)
            no = self.box.addButton('No', QMessageBox.NoRole)

            pos = self.geometry()
            left = pos.left()
            top = pos.top()
            self.box.setGeometry(left + 100, top + 200, 200, 300)
            self.box.show()
            yes.clicked.connect(lambda:self.toGroupChat(currentGroupId))


        # render connected clients
        temp = self.clientList.keys() & clientList.keys()
        # if the client is not change, we just need to update their time
        if( (len(self.clientList) == len(clientList)) & (len(temp) == len(self.clientList))):
            for (ip, port, cname), clientsGroupIds in self.clientList.items():
                diffTime = int((datetime.now()-allClientsTime[(ip,port,cname)]).seconds / 60)
                if (diffTime == 0):
                    diffTime = 'now'
                else:
                    diffTime = str(diffTime) + " mins ago "
                if ((cname == self.client.name) & (ip == self.client.addr.replace("'", "")) & (
                        port == self.client.portAddr)):
                    changes = cname + \
                              " (me) (" + diffTime + ")"
                else:
                    changes = cname + \
                              " (" + diffTime + ")"

                for i in range(self.connectedClients.count()):
                    if changes.split('(')[0] == self.connectedClients.item(i).text().split('(')[0]:
                        if changes != self.connectedClients.item(i).text():
                            self.connectedClients.item(i).setText(changes)
        else: # the client changed, we will render once from the start
            self.connectedClients.clear()

            self.clientList = clientList

            for (ip,port,cname),clientsGroupIds in self.clientList.items():
                diffTime = int((datetime.now()-allClientsTime[(ip,port,cname)]).seconds / 60)
                if (diffTime == 0):
                    diffTime = 'now'
                else:
                    diffTime = str(diffTime) + " mins ago "

                if ((cname == self.client.name) & (ip == self.client.addr.replace("'", "")) & (
                        port == self.client.portAddr)):
                    changes = cname + \
                              " (me) (" + diffTime + ")"
                else:
                    changes = cname + \
                              " (" + diffTime + ")"
                self.connectedClients.addItem(changes)

        # render the chat room
        if(len(self.groupOwner)!= len(groupOwners)):
           self.groupOwner = groupOwners
           self.groupChats.clear()
           for groupId,(ip,port,name) in self.groupOwner.items():
               self.groupChats.addItem("Room "+ str(groupId)+" by "+str(name))







