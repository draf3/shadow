import sys
from PyQt5.QtWidgets import QApplication
import config
from gui import GUI


sys.setrecursionlimit(2000)

if __name__ == '__main__':

    app = QApplication([])
    gui = GUI()
    app.exec_()