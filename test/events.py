from PyQt5.QtCore import QObject, pyqtSignal

class Events(QObject):
    v = pyqtSignal()
    t = pyqtSignal(tuple)
    o = pyqtSignal(object)
    i = pyqtSignal(int)
    f = pyqtSignal(float)
    s = pyqtSignal(str)

