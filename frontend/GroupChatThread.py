import time

from PyQt5.QtCore import QThread, pyqtSignal


class GetGroupChatThread(QThread):
    allClients= pyqtSignal(list)
    messages = pyqtSignal(list)

    def __init__(self, client):
        super().__init__()
        self.Running = True
        self.client = client

    def run(self):
        while self.Running:
            self.client.sendAllClientsSignal()
            data = self.client.recieveData()
            time.sleep(0.15)
            if(type(data[0]) == int):
               if(data[1]!=data[2]):
                   if(type(data[2]) == int ):
                     self.messages.emit(data)
               else:
                   self.Running = False
            else:
                self.allClients.emit(data)

    def stop(self):
        self.Running = False

    def restart(self):
        self.Running = True

