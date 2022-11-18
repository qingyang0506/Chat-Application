
from PyQt5.QtCore import QThread, pyqtSignal


class getAllClientsThread(QThread):
    allClients = pyqtSignal(list)

    def __init__(self, client):
        super().__init__()
        self.Running = True
        self.client = client

    def stop(self):
        self.Running = False

    def restart(self):
        self.Running = True

    def run(self):
        while self.Running:
            data = self.client.getAllClients()
            if(type(data[0])== dict):
                self.allClients.emit(data)
