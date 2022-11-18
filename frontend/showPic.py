

from PyQt5.QtWidgets import (QWidget,  QLabel)

from PyQt5.QtGui import QPixmap


class showPic(QWidget):

    def __init__(self, filename):
        super().__init__()
        self.initUI(filename)

    def initUI(self, filename):
        imglabel = QLabel(self)
        pixmap = QPixmap(filename)
        pic = QPixmap(pixmap)
        imglabel.resize(pic.size())
        imglabel.setPixmap(pic)
        imglabel.setScaledContents(True)


        self.setGeometry(400, 200, 1200, 1200)
        self.show()
