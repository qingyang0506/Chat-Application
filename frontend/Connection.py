
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox)

from frontend.Connected import Connected
from backend.client import Client


class Connection(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        self.setLayout(grid)

        self.ipAddress = QLineEdit()
        self.port = QLineEdit()
        self.nickname = QLineEdit()
        grid.addWidget(QLabel('IP Address:'), 0, 0)
        grid.addWidget(QLabel('Port:'), 1, 0)
        grid.addWidget(QLabel('Nickname:'), 2, 0)

        grid.addWidget(self.ipAddress, 0, 1)
        self.ipAddress.setText("127.0.0.1")
        grid.addWidget(self.port, 1, 1)
        grid.addWidget(self.nickname, 2, 1)

        connectBtn = QPushButton('Connect', self)
        connectBtn.resize(connectBtn.sizeHint())
        connectBtn.clicked.connect(self.Connected)

        quitBtn = QPushButton('Quit', self)
        quitBtn.resize(quitBtn.sizeHint())
        quitBtn.clicked.connect(self.close)

        grid.addWidget(connectBtn, 3, 2)
        grid.addWidget(quitBtn, 3, 3)

        self.setWindowTitle('Chatting Program')
        self.setGeometry(700, 450, 900, 550)
        self.show()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', 'Are you want to quit?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def Connected(self):
        ip_address = self.ipAddress.text()
        portNumber = int(self.port.text())
        nikcName = self.nickname.text()

        if (ip_address == ""):
            client = Client(nikcName, portNumber)
        else:
            client = Client(nikcName, portNumber, ip_address)
        self.window = Connected(self, client)
        self.window.show()
        self.hide()
        self.ipAddress.clear()
        self.nickname.clear()
        self.port.clear()
