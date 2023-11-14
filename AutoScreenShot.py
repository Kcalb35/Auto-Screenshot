# Project Name: Auto Screenshot
# Description: Take screenshot of screen when any change take place.
# Author: Mani (Infinyte7)
# Date: 26-10-2020
# License: MIT

from PIL import ImageChops
from mss import mss

import os
import time
import sys
from datetime import datetime

import tkinter as tk
from tkinter import *
from tkinter import font

import imgcompare

from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image

coord = [0,0,0,0]

class Snippy(QtWidgets.QWidget):
    def __init__(self,root):
        super().__init__()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.setGeometry(0, 0, screen_width, screen_height)
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
        global coord
        self.close()
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())
        coord[0] = x1
        coord[1] = y1
        coord[2] = x2
        coord[3] = y2

class AutoScreenshot:
    def __init__(self, master):
        self.root = master
        
        root.title('Auto Screenshot')
        root.config(bg="white")

        fontRoboto = font.Font(family='Roboto', size=16, weight='bold')

        # project name label     
        projectTitleLabel = Label(root, text="Auto Screenshot")
        projectTitleLabel.config(font=fontRoboto, bg="white", fg="#5599ff")
        projectTitleLabel.pack(padx="10")

        # start button
        btn_start = Button(root, text="Start", command=self.start)
        btn_start.config(highlightthickness=0, bd=0, fg="white", bg="#5fd38d",
                         activebackground="#5fd38d", activeforeground="white", font=fontRoboto)
        btn_start.pack(padx="10", fill=BOTH)

        # close button
        btn_start = Button(root, text="Close", command=self.close)
        btn_start.config(highlightthickness=0, bd=0, fg="white", bg="#f44336",
                         activebackground="#ff7043", activeforeground="white", font=fontRoboto)
        btn_start.pack(padx="10", pady="10", fill=BOTH)
      
    def start(self):
        # Create folder to store images
        directory = "Screenshots"
        self.new_folder = directory + "/" + datetime.now().strftime("%Y_%m_%d-%I_%M_%p")

        # all images to one folder
        if not os.path.exists(directory):
            os.makedirs(directory)

        # new folder for storing images for current session
        if not os.path.exists(self.new_folder):
            os.makedirs(self.new_folder)

        # Run ScreenCords.py and get cordinates
        self.app = QtWidgets.QApplication.instance()
        if not self.app:
            self.app = QtWidgets.QApplication(sys.argv)

        window = Snippy(self.root)
        window.show()
        self.app.aboutToQuit.connect(self.app.deleteLater)
        self.app.exec_()
        print("coords:",coord)

        # cordinates for screenshots and compare
        self.cords = coord

        # save first image
        img1 = self.get_img()
        now = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        fname = self.new_folder + "/ScreenShots" + now + ".png"
        img1.save(fname)
        print("Screenshot taken")

        # maintain a reference image
        self.ref_img = img1 

        # start taking screenshot of next images
        self.take_screenshots()       

    def get_img(self):
        with mss() as sct:
            monitor = {"top": self.cords[1], "left": self.cords[0], "width": self.cords[2] - self.cords[0], "height": self.cords[3] - self.cords[1]}
            img = sct.grab(monitor)
            img_img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
        return img_img

    def take_screenshots(self):
        #imgcompare param
        tolerance = 3

        # grab first and second image
        # img1 now becomes self.img1, to have a consistent ref
        time.sleep(1) # check screen every x seconds
        img2 = self.get_img()
        img_is_equal = imgcompare.is_equal(self.ref_img, img2, tolerance)

    
        if not img_is_equal:
            now = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
            fname = self.new_folder + "/ScreenShots" + now + ".png"
            img2.save(fname)
            print("Screenshot taken")

            self.ref_img = img2

        root.after(5, self.take_screenshots)

    def close(self):
        self.root.destroy()

if __name__ == "__main__":  
    root = tk.Tk()
    gui = AutoScreenshot(root)
    root.mainloop()
