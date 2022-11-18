from PyQt5.QtWidgets import (QApplication, QWidget)
from frontend.Connection import Connection
import sys


class Start(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.window = Connection()
        self.window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Start()
    sys.exit(app.exec_())
