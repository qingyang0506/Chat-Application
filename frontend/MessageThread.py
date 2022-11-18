from PyQt5.QtCore import QThread, pyqtSignal


class MessagesThread(QThread):
    messages = pyqtSignal(list)

    def __init__(self, client):
        super().__init__()
        self.Running = True
        self.client = client

    def run(self):
        while self.Running:
            data = self.client.recieveData()
            if((type(data[2]) == tuple) & (data[1]!=data[2])):
               self.messages.emit(data)


    def stop(self):
        self.Running = False

    def restart(self):
        self.Running = True
