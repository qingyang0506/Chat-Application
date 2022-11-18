import time

from PyQt5.QtWidgets import (QWidget, QLineEdit,QFileDialog,
                             QPushButton, QHBoxLayout, QVBoxLayout, QLabel)
from PyQt5.QtGui import QFont, QPixmap


from datetime import datetime

from frontend.MessageThread import MessagesThread
from frontend.showPic import showPic


class oneToOne(QWidget):

    def __init__(self, clientSelf, clientTalk, previousScreen, thread):
        super().__init__()
        self.initUI(clientSelf, clientTalk, previousScreen, thread)

    def initUI(self, clientSelf, clientTalk, previousScreen, thread):
        self.connected = previousScreen
        self.client = clientSelf
        self.clientTalk = clientTalk
        self.allClientsThread = thread
        sendBtn = QPushButton('Send', self)
        sendBtn.resize(sendBtn.sizeHint())
        sendBtn.clicked.connect(self.sendMessage)

        sendImageBtn = QPushButton('Send Image', self)
        sendImageBtn.resize(sendImageBtn.sizeHint())
        sendImageBtn.clicked.connect(self.sendImage);

        closeBtn = QPushButton('Close', self)
        closeBtn.resize(closeBtn.sizeHint())
        closeBtn.clicked.connect(self.close)

        self.sendBox = QLineEdit()

        self.messageThread = MessagesThread(self.client)
        self.messageThread.messages.connect(self.updateChat)
        self.messageThread.start()

        hbox = QHBoxLayout()
        hbox.addWidget(self.sendBox)
        hbox.addWidget(sendBtn)
        hbox.addWidget(sendImageBtn)
        vbox = QVBoxLayout()
        self.chatContent = QVBoxLayout()


        title = QLabel("Chat with "+ clientTalk[2])
        title.setFont(QFont("Roman times",10,QFont.Bold))
        vbox.addWidget(title)
        vbox.addLayout(self.chatContent)
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addWidget(closeBtn)

        self.setWindowTitle('Chatting Program')
        pos = self.connected.geometry()
        self.setGeometry(pos.left(),pos.top(),650,800)
        self.setLayout(vbox)

    def close(self):
        self.client.sendMessage([1,self.client.getInfo(),self.client.getInfo(),"quit"])
        self.messageThread.stop()
        time.sleep(0.5)
        self.hide()
        self.connected.show()
        self.allClientsThread.restart()
        self.allClientsThread.start()

    def sendMessage(self):
        text = self.sendBox.text()
        self.sendBox.clear()
        msg = "Me ("+ datetime.now().strftime("%H:%M") +"): " + text
        self.chatContent.addWidget(QLabel(msg))
        sendMsg = [1,self.client.getInfo(),self.clientTalk,text]
        self.client.sendMessage(sendMsg)

    def renderImage(self,filename,msg):
        if(filename == ""):
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
        self.renderImage(imagPath,msg)
        sendMsg = [2,self.client.getInfo(),self.clientTalk,imagPath]
        self.client.sendMessage(sendMsg)

    def view(self, filename):

        self.window = showPic(filename)
        self.window.show()

    def download(self, pic):
        img = pic.toImage()

        fdir, ftype = QFileDialog.getSaveFileName(self, "Save Image",
                                                  "./", "Image Files (*.jpg *.gif *.png)")
        img.save(fdir)

    def updateChat(self, messages):
        if(messages[0]==1):# receive text message
            clientName = messages[1][2]
            if((messages[2] == self.client.getInfo()) & (messages[1] == self.clientTalk)):
                msg = clientName + "("+ datetime.now().strftime("%H:%M") +"): "+ messages[3]
                self.chatContent.addWidget(QLabel(msg))
        else: # receive image
            clientName = messages[1][2]
            if (( messages[2] == self.client.getInfo()) & (messages[1] == self.clientTalk)):
                msg = clientName + "("+ datetime.now().strftime("%H:%M") +"): Send Image"
                self.renderImage(messages[3],msg)