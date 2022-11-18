import time

from PyQt5.QtWidgets import (QListWidget, QWidget, QLineEdit,QFileDialog,
                             QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QLabel)
from datetime import datetime

from PyQt5.QtGui import QFont, QPixmap

from frontend.invite import Invite
from frontend.GroupChatThread import GetGroupChatThread
from frontend.showPic import showPic


class GroupChat(QWidget):

    def __init__(self, client, groupId, groupOwner,previousScreen,thread):
        super().__init__()
        self.initUI(client,groupId,groupOwner,previousScreen,thread)

    def initUI(self,client,groupId,groupOwner,previousScreen,thread):

        self.client = client
        self.connected = previousScreen
        self.groupId = groupId
        self.groupOwner = groupOwner
        self.getAllClientsThread = thread

        self.groupMember = {}


        sendBtn = QPushButton('Send', self)
        sendBtn.resize(sendBtn.sizeHint())
        sendBtn.clicked.connect(self.sendMessage)

        sendImage = QPushButton('Send Image', self)
        sendImage.resize(sendImage.sizeHint())
        sendImage.clicked.connect(self.sendImage)

        closeBtn = QPushButton('Close', self)
        closeBtn.resize(closeBtn.sizeHint())
        closeBtn.clicked.connect(self.close)

        self.sendBox = QLineEdit()

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.sendBox)
        hbox1.addWidget(sendBtn)
        hbox1.addWidget(sendImage)
        vbox1 = QVBoxLayout()
        self.chatContent = QVBoxLayout()
        self.groupChatLabel = QLabel(
            "Room " + str(groupId) + " by " + self.groupOwner)
        self.groupChatLabel.setFont(QFont("Roman times",10,QFont.Bold))
        vbox1.addWidget(self.groupChatLabel)
        vbox1.addLayout(self.chatContent)
        vbox1.addStretch(1)
        vbox1.addLayout(hbox1)
        vbox1.addWidget(closeBtn)

        vbox2 = QVBoxLayout()
        inviteBtn = QPushButton('Invite', self)
        inviteBtn.resize(inviteBtn.sizeHint())
        inviteBtn.clicked.connect(self.invite)

        self.groupChatThread = GetGroupChatThread(self.client)
        self.groupChatThread.allClients.connect(
            self.renderGroupMember)
        self.groupChatThread.messages.connect(self.updateChatContent)
        self.groupChatThread.start()


        self.members = QListWidget()
        vbox2.addWidget(QLabel("Members"))
        vbox2.addWidget(self.members)
        vbox2.addWidget(inviteBtn)

        hbox2 = QHBoxLayout()
        hbox2.addLayout(vbox1)
        hbox2.addLayout(vbox2)


        self.setWindowTitle('Chatting Program')
        pos = self.connected.geometry()
        self.setGeometry(pos.left(),pos.top(),800,800)
        self.setLayout(hbox2)

    def renderGroupMember(self,allClients):
        clientList = allClients[0]
        groupMember = {}

        for i in range(len(list(clientList))):
            key = list(clientList)[i]
            for id in clientList[key]:
                if(id == self.groupId):
                    groupMember[key] = 1;
                    break

        if(len(self.groupMember) != len(groupMember)):
            self.members.clear()
            self.groupMember = groupMember
            for (ip,port,name), val in self.groupMember.items():
                nameItems = str(name)
                if(self.groupOwner == name):
                    nameItems += " (host)"
                if (name == self.client.getMyName()):
                    nameItems += " (me) "
                self.members.addItem(nameItems)


    def sendMessage(self):
        text = self.sendBox.text()
        self.sendBox.clear()
        msg = "Me (" + datetime.now().strftime("%H:%M") + "): " + text
        self.chatContent.addWidget(QLabel(msg))
        sendMsg = [1,self.client.getInfo(),self.groupId,text]
        self.client.sendMessage(sendMsg)

    def renderImage(self,filename,msg):
        if(filename==""):
            return
        imglabel = QLabel()
        pixmap = QPixmap(filename)
        pic = QPixmap(pixmap)
        imglabel.setFixedSize(200, 200)
        imglabel.setPixmap(pic)
        imglabel.setScaledContents(True)
        vbox = QVBoxLayout()
        info = QLabel(msg)
        hbox = QHBoxLayout()
        view = QPushButton("view")
        view.clicked.connect(lambda: self.view(filename))
        download = QPushButton("download")
        download.clicked.connect(lambda: self.download(pic))
        hbox.addWidget(imglabel)
        hbox.addWidget(view)
        hbox.addWidget(download)
        vbox.addWidget(info)
        vbox.addLayout(hbox)
        self.chatContent.addLayout(vbox)

    def sendImage(self):
        filename = QFileDialog.getOpenFileName(
            self, "open file", 'c\\', "Image file (*.jpg *.gif *.png)")
        imagPath = filename[0]
        msg = "Me (" + datetime.now().strftime("%H:%M") + "): Send Image"
        self.renderImage(imagPath, msg)
        sendMsg = [2, self.client.getInfo(), self.groupId, imagPath]
        self.client.sendMessage(sendMsg)

    def view(self, filename):

        self.window = showPic(filename)
        self.window.show()

    def download(self, pic):
        img = pic.toImage()

        fdir, ftype = QFileDialog.getSaveFileName(self, "Save Image",
                                                  "./", "Image Files (*.jpg *.gif *.png)")
        img.save(fdir)

    def updateChatContent(self,message):
       if(message[0]==1):#receive text message
           if(message[2]==self.groupId):
               msg = message[1][2] + "("+ datetime.now().strftime("%H:%M") + "): " + message[3]
               self.chatContent.addWidget(QLabel(msg))
       else:# receive img
           if(message[2]==self.groupId):
               msg = message[1][2] + "("+ datetime.now().strftime("%H:%M") + "): Send Image"
               self.renderImage(message[3],msg)

    def invite(self):
        self.groupChatThread.stop()
        time.sleep(0.5)
        self.client.sendMessage([1, self.client.getInfo(), self.client.getInfo(), "invite"])
        self.window = Invite(self.client,self.groupId,self.groupOwner,self,self.groupChatThread)
        self.window.show()
        self.hide()


    def close(self):
        self.groupChatThread.stop()
        self.client.sendMessage([1, self.client.getInfo(), self.client.getInfo(), "quit"])
        time.sleep(0.5)
        self.hide()
        self.connected.show()
        self.getAllClientsThread.restart()
        self.getAllClientsThread.start()


