import sys
from PyQt5.QtWidgets import QApplication
from gui import GUI


if __name__ == '__main__':
    sys.setrecursionlimit(2000)
    app = QApplication([])
    gui = GUI()
    app.exec_()