# Project Name: Auto Screenshot
# Description: Take screenshot of screen when any change take place.
# Author: Mani (Infinyte7)
# Date: 26-10-2020
# License: MIT

from PIL import Image
from mss import mss
import os
import sys
from datetime import datetime
import imgcompare
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QTimer

class Snippy(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.coord = [0, 0, 0, 0]

        screen_rect = QApplication.desktop().screenGeometry()
        self.setGeometry(0, 0, screen_rect.width(), screen_rect.height())
        self.setWindowTitle('ScreenShot')
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setWindowOpacity(0.15)
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('red'), 1))
        qp.setBrush(QtGui.QColor(128, 128, 255, 128))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.close()
        x1, y1 = min(self.begin.x(), self.end.x()), min(self.begin.y(), self.end.y())
        x2, y2 = max(self.begin.x(), self.end.x()), max(self.begin.y(), self.end.y())
        self.coord = [x1, y1, x2, y2]

    def getCoords(self):
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())
        return [x1, y1, x2, y2]

class AutoScreenshot(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.all_images = []
    def init_ui(self):
        self.setWindowTitle('Auto Screenshot')
        self.setGeometry(300, 300, 250, 150)

        layout = QVBoxLayout()

        self.label = QLabel("Auto Screenshot")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label)

        self.btn_start = QPushButton("Start", self)
        self.btn_start.clicked.connect(self.start)
        layout.addWidget(self.btn_start)

        self.btn_close = QPushButton("Close", self)
        self.btn_close.clicked.connect(self.close)
        layout.addWidget(self.btn_close)

        self.setLayout(layout)
        
    def start(self):
        directory = "Screenshots"
        self.new_folder = directory + "/" + datetime.now().strftime("%Y_%m_%d-%I_%M_%p")
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(self.new_folder):
            os.makedirs(self.new_folder)

        self.snippy = Snippy()
        self.snippy.exec_()

        self.cords = self.snippy.coord
        self.save_image(self.get_img())

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.take_screenshots)
        self.timer.start(1000)

    def get_img(self):
        with mss() as sct:
            monitor = {"top": self.cords[1], "left": self.cords[0], "width": self.cords[2] - self.cords[0], "height": self.cords[3] - self.cords[1]}
            img = sct.grab(monitor)
            return Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")

    def take_screenshots(self):
        tolerance = 3
        new_img = self.get_img()

        if not self.all_images:
            self.save_image(new_img)
        elif all(not imgcompare.is_equal(img, new_img, tolerance) for img in self.all_images):
            self.save_image(new_img)

    def save_image(self, img):
        now = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        fname = self.new_folder + "/ScreenShots" + now + ".png"
        img.save(fname)
        print("Screenshot taken")
        self.all_images.append(img)

if __name__ == "__main__":  
    app = QApplication(sys.argv)
    ex = AutoScreenshot()
    ex.show()
    sys.exit(app.exec_())
